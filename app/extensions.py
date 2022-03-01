from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from werkzeug.local import LocalProxy
from app.common.logging import get_log
from app.jwt_callbacks import expired_token_callback, invalid_token_callback

db = SQLAlchemy()
jwt = JWTManager()
logger = LocalProxy(get_log)


jwt.expired_token_loader(expired_token_callback)
jwt.invalid_token_loader(invalid_token_callback)
