from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from werkzeug.local import LocalProxy
from app.common.logging import get_log

db = SQLAlchemy()
jwt = JWTManager()
logger = LocalProxy(get_log)
