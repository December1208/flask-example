from flask import Flask
import importlib
from app.extensions import db, jwt

ADDONS = [

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

    # import models
    import_models()

    db.init_app(_app)

    jwt.init_app(_app)

    return _app


app = create_app()
