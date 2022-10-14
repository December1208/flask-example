from app.models.base import BaseModel
from common.extensions import db


class Account(BaseModel):
    email = db.Column(db.String(64), index=True, nullable=False, doc="邮箱")
    salt = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    country_code = db.Column(db.String(8), doc='国家代码', nullable=True)
    phone_number = db.Column(db.String(16), doc='手机号', nullable=True, index=True)
    last_login_at = db.Column(db.BigInteger, nullable=True, doc='上次登录时间')


class Profile(BaseModel):
    username = db.Column(db.String(64), index=True, nullable=False)
    account_id = db.Column(db.Integer, index=True)
