from common.extensions import db
from utils import time as time_util, helper


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True, unique=True, default=helper.uuid)
    created_at = db.Column(db.Integer, default=time_util.int_timestamp)
    updated_at = db.Column(db.Integer, default=time_util.int_timestamp, onupdate=time_util.int_timestamp)
