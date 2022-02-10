from flask import Flask
import importlib
from flask_jwt import JWT

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

    return _app


app = create_app()
