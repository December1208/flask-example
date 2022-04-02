import hashlib
import random
import string
import time
import uuid as uuid_
from collections import defaultdict

from app.common.exception import APIException, Error
from app.extensions import db, logger
from app.settings import setting
from app.utils import time as custom_time

ALLOWED_CHARS = string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase


def uuid():
    return uuid_.uuid4().hex


def uuid_str():
    return str(uuid_.uuid4())


def str2bool(v):
    if v is None:
        v = ''
    return v.lower() in ("yes", "true", "t", "1")


def validate_str(key, value, validation_rules, key_verbose_name=None):
    value = str(value)
    if validation_rules:
        max_length = validation_rules.get('max_length', None)
        min_length = validation_rules.get('min_length', None)
        result = str(value)
        if max_length and len(result) > max_length:
            raise APIException(detail=f"{key_verbose_name or key} 超过了最大长度 {max_length} 限制",
                               error_code=Error.InvalidParamsError[0])
        if min_length and len(result) < min_length:
            raise APIException(detail=f"{key_verbose_name or key} 超过了最小长度 {min_length} 限制",
                               error_code=Error.InvalidParamsError[0])
    return value


def validate_list(key, value, validation_rules, key_verbose_name=None):
    value = list(value)
    if validation_rules:
        element_type = validation_rules.get('element_type', None)
        if element_type is str:
            value = [str(v) for v in value]
        if element_type is dict:
            value = [dict(v) for v in value]

    return value


def convert_type(key, value, _type, validation_rules, key_verbose_name=None):
    type2validate_str = {
        str: validate_str,
        list: validate_list,
    }
    func = type2validate_str.get(_type)
    if func is None:
        return _type(value)

    return func(key, value, validation_rules, key_verbose_name=key_verbose_name)


def get_param(params, key, _type, nullable=False, default=None, extra_validation_rules=None, key_verbose_name=None):
    # 获得key 对应的值，处理params为空的情况
    if not params and nullable:
        return default
    val = params.get(key, None)
    logger.debug(f'get value by key [{key}], need type: [{_type}], get type {type(val)}')

    # 处理值为空的情况
    if (val is None or val == '') and nullable:
        logger.debug(f'value is None and nullable, return default [{default}]')
        return default
    elif val is None:
        raise APIException(detail=f"{key_verbose_name or key} 参数不能为空", error_code=Error.InvalidParamsError[0])

    # 对值做类型处理
    logger.debug('has value, try to check type')
    # 对bool做特殊判断
    if _type is bool and (isinstance(val, str) or val is None):
        return str2bool(val)
    try:
        return convert_type(key, val, _type, extra_validation_rules, key_verbose_name=key_verbose_name)
    except ValueError as e:
        logger.info('param type error, detail: {}, {}, {}'.format(type(e), e, e.args))
        raise APIException(detail=f"{key_verbose_name or key} 参数类型错误", error_code=Error.InvalidParamsError[0])


def get_random_string(length=12, allowed_chars=ALLOWED_CHARS):
    _random = random.SystemRandom()
    _random.seed(
        hashlib.sha256(
            ('%s%s%s' % (random.getstate(), time.time(), setting.SECRET_KEY)).encode()
        ).digest()
    )

    return ''.join(random.choice(allowed_chars) for i in range(length))


def safe_commit():
    try:
        db.session.commit()
    except Exception as e:
        logger.warning("DB sql commit error, detail: {}".format(e))
        db.session.rollback()
        raise APIException(error=Error.DBError)


def build_statistics_data(queryset, start_at, end_at, time_field='created_at', identity_field='id'):
    """
    将数据根据日期统计
    queryset中的元素应当包含time_field, identity_field
    :param queryset: 数据
    :param start_at: 起始时间
    :param end_at: 结束时间
    :param time_field:  时间字段的名称
    :param identity_field: 唯一值字段的名称
    :return:
    """

    date2count = defaultdict(int)
    date2identity_value = defaultdict(set)
    for time_stamp_of_date in range(start_at, end_at, custom_time.PER_DAY_SECONDS):
        date2count[time_stamp_of_date] = 0

    for instance in queryset:
        time_stamp_of_date = custom_time.day_begin(getattr(instance, time_field))
        identity_value = getattr(instance, identity_field)
        if identity_value in date2identity_value[time_stamp_of_date]:
            continue
        date2count[time_stamp_of_date] += 1
        date2identity_value[time_stamp_of_date].add(identity_value)

    result = [
        {
            "date_timestamp": key,
            "count": value
        }
        for key, value in date2count.items()
    ]
    return result


def int_or_none(int_):
    try:
        return int(int_)
    except:
        return None


def str_or_none(str_):
    try:
        return str(str_)
    except:
        return None
