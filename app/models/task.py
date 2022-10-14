from common.extensions import db
from app.models.base import BaseModel


class TaskGroup(BaseModel):
    name = db.Column(db.String(64), doc="分组名称")
    description = db.Column(db.Text, doc="分组描述")


class Task(BaseModel):
    name = db.Column(db.String(64), doc="任务名称")
    progress_id = db.Column(db.Integer, doc="进度状态", index=True)
    description = db.Column(db.Text, doc="任务描述")
    priority = db.Column(db.Integer, doc="任务优先级")
    planned_start_at = db.Column(db.BigInteger, doc="计划开始时间")
    planned_end_at = db.Column(db.BigInteger, doc="计划结束时间")
    actual_start_at = db.Column(db.BigInteger, doc="实际开始时间")
    actual_end_at = db.Column(db.BigInteger, doc="实际结束时间")
    document_url = db.Column(db.JSON, doc="文档地址")
