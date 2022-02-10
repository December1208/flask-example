import time


def int_timestamp() -> int:
    """
    返回现在的int型的时间戳， 秒
    :return: 返回现在的int型的时间戳
    """
    return int(time.time())


def int_millisecond_timestamp() -> int:
    """
    返回现在的int型的时间戳， 毫秒
    :return:
    """
    return int(time.time() * 1000)
