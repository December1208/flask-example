import importlib

from flask import Flask

from app.extensions import db, jwt
from app.jwt_callbacks import expired_token_callback, invalid_token_callback
from app.routers import init_router
from app.settings import setting

ADDONS = [
    'account',
    'event_schedule'
]


def import_models():
    for addon in ADDONS:
        module_path = f'app.models.{addon}'
        try:
            importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise RuntimeError(f"Not found {addon}")


def create_app():

    _app = Flask(__name__)
    _app.config.from_object(setting)

    db.init_app(_app)

    # import models
    import_models()

    jwt.init_app(_app)
    jwt.expired_token_loader(expired_token_callback)
    jwt.invalid_token_loader(invalid_token_callback)

    init_router(_app)

    return _app


app = create_app()
