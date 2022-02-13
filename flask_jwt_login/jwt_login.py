from collections import OrderedDict

import jwt
from flask import current_app, request, Flask, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy

from flask_jwt_login.constants import EXTENSION_KEY, CONFIG_DEFAULTS
from flask_jwt_login.exception import JWTError
from flask_jwt_login.token import Token, RefreshToken, AccessToken

_jwt = LocalProxy(lambda: current_app.extensions[EXTENSION_KEY])


def _default_jwt_payload_handler(identity, token_cls: Token):
    payload = token_cls.get_payload(identity)

    return payload


def _default_jwt_decode_handler(token, token_cls):
    try:
        return jwt.decode(token, token_cls.jwt_secret_key, algorithms=[token_cls.jwt_algorithm, ])
    except jwt.ExpiredSignatureError:
        raise JWTError("ExpiredSignatureError", "expire signature")
    except jwt.InvalidTokenError:
        raise JWTError("UnknownError", "unknown signature")


def _default_jwt_encode_handler(identity, token_cls):
    payload = _jwt.jwt_payload_callback(identity, token_cls)

    return jwt.encode(payload=payload, key=token_cls.jwt_secret_key, algorithm=token_cls.jwt_algorithm)


def _default_request_handler():
    auth_header_value = request.headers.get('Authorization', None)
    if not auth_header_value:
        raise JWTError('Invalid JWT', "invalid jwt", 400)
    parts = auth_header_value.split()

    return parts[1]


def _default_error_handler(error):
    return jsonify(OrderedDict([
        ('status_code', error.status_code),
        ('error', error.error),
        ('description', error.description),
    ])), error.status_code


def _default_unauthorized_handler():
    return jsonify({
        'code': 400,
        'detail': "invalid user",
        'data':None,
        'success': False
    }), 400


class JWT(object):
    def __init__(self, app=None):
        self.access_token_cls = AccessToken
        self.refresh_token_cls = RefreshToken

        self.jwt_payload_callback = _default_jwt_payload_handler
        self.jwt_decode_callback = _default_jwt_decode_handler
        self.jwt_encode_callback = _default_jwt_encode_handler

        self.jwt_error_callback = _default_error_handler
        self.request_handler = _default_request_handler
        self._user_callback = None
        self.unauthorized_callback = _default_unauthorized_handler

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        for k, v in CONFIG_DEFAULTS.items():
            app.config.setdefault(k, v)
        app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])
        app.errorhandler(JWTError)(self._jwt_error_callback)
        self.init_access_token_cls()
        self.init_refresh_token_cls()

        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}

        app.extensions[EXTENSION_KEY] = self

    def init_access_token_cls(self):
        self.access_token_cls.jwt_algorithm = current_app.config.get('JWT_ALGORITHM')
        self.access_token_cls.jwt_secret_key = current_app.config.get('JWT_SECRET_KEY')
        self.access_token_cls.lifetime = current_app.config.get('JWT_ACCESS_TOKEN_LIFETIME')
        self.access_token_cls.not_before_delta = current_app.config.get('JWT_NOT_BEFORE_DELTA')

    def init_refresh_token_cls(self):
        self.refresh_token_cls.jwt_algorithm = current_app.config.get('JWT_ALGORITHM')
        self.refresh_token_cls.jwt_secret_key = current_app.config.get('JWT_SECRET_KEY')
        self.refresh_token_cls.lifetime = current_app.config.get('JWT_REFRESH_TOKEN_LIFETIME')
        self.access_token_cls.not_before_delta = current_app.config.get('JWT_NOT_BEFORE_DELTA')

    def _jwt_error_callback(self, error):
        return self.jwt_error_callback(error)

    def _load_identity(self):
        if self.request_handler is None or self._user_callback is None:
            raise Exception(
                "Miss request handler or user loader"
            )
        token = self.request_handler()
        payload = self.jwt_encode_callback(token, self.access_token_cls)
        user = None
        user_id = payload.get('user_id')
        if user_id is not None:
            identity = self._user_callback(user_id)

        self._update_request_context_with_user(user)

    @staticmethod
    def _update_request_context_with_user(user=None):
        ctx = _request_ctx_stack.top
        ctx.user = user

    def user_loader(self, callback):
        self._user_callback = current_app
        return callback.top

    def unauthorized(self, callback):
        self.unauthorized_callback = callback
