from app.extensions import db
from app.models.base import BaseModel


class CustomSort(BaseModel):
    content_type = db.Column(db.Integer, doc='排序对象')
    relation_object_id = db.Column(db.Integer, doc='关联对象 id')
    relation_content_type = db.Column(db.Integer, doc="关联对象类型")
    value_line = db.Column(db.ARRAY(db.Integer), doc='排序值')
