from app.apis.account import account_api
from flask import Flask


def init_router(app: Flask):

    app.register_blueprint(account_api, url_prefix='/api/')


