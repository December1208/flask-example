from app.models.base import BaseModel
from app.extensions import db


class EventSchedule(BaseModel):
    event_type = db.Column(db.Integer, doc="事件类型", index=True)
    event_params = db.Column(db.JSON, doc="事件类型的参数")
    trigger_time = db.Column(db.Integer, doc="触发时间", index=True)
    done_time = db.Column(db.Integer, doc="完成时间")
    event_status = db.Column(db.Integer, doc="事件状态", index=True)


class EventRelation(BaseModel):
    # constants.base.ContentType
    content_type = db.Column(db.Integer, doc="关联对象类型", index=True)
    object_id = db.Column(db.Integer, doc="关联对象id", index=True)
    event_id = db.Column(db.Integer, doc="事件id", index=True)


