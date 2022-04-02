
class EventStatus:
    # 事件状态

    PENDING = 1  # 待执行
    RECEIVED = 2  # 已被从数据库中取出
    STARTED = 3  # 已经开始执行
    SUCCESS = 4  # 执行成功
    FAILURE = 5  # 执行失败
    REVOKED = 6  # 被撤销
    RETRY = 7  # 重试


EVENT_STATUS_DISPLAY_NAME = {
    EventStatus.PENDING: "待执行",
    EventStatus.RECEIVED: "已收到，准备执行",
    EventStatus.STARTED: "开始执行",
    EventStatus.SUCCESS: "执行成功",
    EventStatus.FAILURE: "执行失败",
    EventStatus.REVOKED: "撤销",
    EventStatus.RETRY: "重试",
}


class EventType:
    # 事件类型
    pass
