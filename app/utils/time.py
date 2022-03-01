import datetime
import functools
import time

from dateutil import parser

from app.extensions import logger

PER_MINUTE_SECONDS = 60
PER_HOUR_SECONDS = 3600
PER_DAY_SECONDS = 24 * 3600
ONE_MONTH = PER_DAY_SECONDS * 30
THREE_MONTH = ONE_MONTH * 3
SIX_MONTH = ONE_MONTH * 6
ONE_YEAR = ONE_MONTH * 12
DATE_FORMAT_STR = '%Y-%m-%d'
DATETIME_FORMAT_STR = '%Y-%m-%d %H:%M:%S'
WEEKDAY_DICT = {
    0: '星期一',
    1: '星期二',
    2: '星期三',
    3: '星期四',
    4: '星期五',
    5: '星期六',
    6: '星期天',
}


def int_timestamp() -> int:
    """
    返回现在的int型的时间戳， 秒
    :return: 返回现在的int型的时间戳
    """
    return int(time.time())


def int_timestamp_millisecond() -> int:
    """
    返回现在的int型的时间戳， 毫秒
    :return:
    """
    return int(time.time() * 1000)


def after_second(second: int, t=None) -> int:
    """返回经过{second}秒的时间戳"""
    if t is None:
        t = int_timestamp()
    return t + second


def before_second(second: int, t=None) -> int:
    """返回{second}秒之前的时间戳"""
    if t is None:
        t = int_timestamp()
    return t - second


def target_timestamp(time_, format_):
    """获取给定时间的时间戳"""
    time_stamp = time.mktime(time.strptime(time_, format_))
    return int(time_stamp)


def day_begin(t=None, timezone=8) -> int:
    """
    :param t: 时间戳
    :param timezone: 时区
    获取今天0点的时间戳
    """
    if t is None:
        t = int_timestamp()
    return ((t + timezone * PER_HOUR_SECONDS) // PER_DAY_SECONDS) * PER_DAY_SECONDS - (timezone * PER_HOUR_SECONDS)


def day_end(t=None, timezone=8):
    """
    返回给定时间的24点（第二天的0点）的时间戳
    :param t: 时间戳，int/float/str都可
    :param timezone: 时区
    :return: int型时间戳
    """
    return day_begin(t, timezone) + PER_DAY_SECONDS


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print_args = str(args) + str(kwargs)
        print_args = print_args[: 1000] + '...' if len(print_args) > 1000 else print_args
        logger.info(f'func {func.__name__} cost {end - start} seconds, args & kwargs: {print_args}')
        return result

    return wrapper


def repr_seconds(seconds, short=False, in_chinese=False):
    if not in_chinese:
        seconds = round(seconds)
        repr_str = str(datetime.timedelta(seconds=seconds))
        if not short:
            return repr_str
        if seconds < 60:
            return repr_str[-4:]
        return repr_str.lstrip('0:')

    if seconds < 1:
        return '不足 1 秒'
    seconds = round(seconds)
    if seconds < 60:
        return f'{seconds} 秒'
    minutes = seconds // 60
    if minutes < 60:
        return f'{minutes} 分 {seconds % 60} 秒'
    hours = minutes // 60
    return f'{hours} 小时 {minutes % 60} 分 {seconds % 60} 秒'


def format_timestamp(time_, format_string='%Y-%m-%d %H:%M:%S'):
    """
    将当前时间戳转换为对应格式的时间字符串,
    """
    time_array = time.localtime(time_)
    return time.strftime(format_string, time_array)


def parse_datetime_str(datetime_str):
    dt = parser.parse(datetime_str)
    return dt


def format_time_interval(start_at: int, end_at: int):
    """将开始时间和结束时间格式化为 月-日(星期几) 时:分～时:分"""
    assert end_at >= start_at, 'end_at < start_at'

    start_at_datetime = datetime.datetime.fromtimestamp(start_at)
    end_at_datetime = datetime.datetime.fromtimestamp(end_at)

    return '{}-{}({}) {}~{}'.format(
        start_at_datetime.month,
        start_at_datetime.day,
        WEEKDAY_DICT.get(start_at_datetime.weekday()),
        datetime.datetime.strftime(start_at_datetime, '%H:%M'),
        datetime.datetime.strftime(end_at_datetime, '%H:%M')
    )
