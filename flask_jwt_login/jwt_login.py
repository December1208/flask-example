from collections import OrderedDict

import jwt
from flask import current_app, request, Flask, jsonify
from werkzeug.local import LocalProxy

from flask_jwt_login.exception import JWTError
from flask_jwt_login.token import Token, RefreshToken, AccessToken

CONFIG_DEFAULTS = {
    'JWT_ALGORITHM': 'HS256',
    'JWT_LEEWAY': 10,
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_ACCESS_TOKEN_LIFETIME': 5 * 60,
    'JWT_IDENTITY_CLAIM': 'identity',
    'JWT_REFRESH_TOKEN_LIFETIME': 60 * 60 * 24 * 7,
    'JWT_NOT_BEFORE_DELTA': 0,
}


_jwt = LocalProxy(lambda: current_app.extensions['jwt-login'])


def _default_jwt_payload_handler(identity, token_cls: Token):
    payload = token_cls.get_payload(identity)

    return payload


def _default_jwt_decode_handler(token, token_cls: Token):
    try:
        return jwt.decode(token, token_cls.jwt_secret_key, algorithms=[token_cls.jwt_algorithm, ])
    except jwt.InvalidSignatureError:
        raise JWTError("InvalidSignatureError", "invalid signature")
    except jwt.ExpiredSignatureError:
        raise JWTError("ExpiredSignatureError", "expire signature")
    except Exception as e:
        raise JWTError("UnknownError", "unknown signature")


def _default_jwt_encode_handler(identity, token_cls: Token):
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


class JWT(object):
    def __init__(self, app=None):
        self.access_token_cls = AccessToken
        self.refresh_token_cls = RefreshToken

        self.jwt_payload_callback = _default_jwt_payload_handler
        self.jwt_decode_callback = _default_jwt_decode_handler
        self.jwt_encode_callback = _default_jwt_encode_handler

        self.jwt_error_callback = _default_error_handler
        self.request_handler = _default_request_handler

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        for k, v in CONFIG_DEFAULTS.items():
            app.config.setdefault(k, v)
        app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])
        app.errorhandler(JWTError)(self._jwt_error_callback)
        self.init_access_token_cls()
        self.init_refresh_token_cls()

    def init_access_token_cls(self):
        self.access_token_cls.jwt_algorithm = current_app.config.get('JWT_ALGORITHM')
        self.access_token_cls.jwt_secret_key = current_app.config.get('JWT_SECRET_KEY')
        self.access_token_cls.jwt_exp_claim = current_app.config.get('JWT_EXP_CLAIM')
        self.access_token_cls.jwt_jti_claim = current_app.config.get('JWT_JTI_CLAIM')
        self.access_token_cls.jwt_identity_claim = current_app.config.get('JWT_IDENTITY_CLAIM')
        self.access_token_cls.lifetime = current_app.config.get('JWT_ACCESS_TOKEN_LIFETIME')

    def init_refresh_token_cls(self):
        self.refresh_token_cls.jwt_algorithm = current_app.config.get('JWT_ALGORITHM')
        self.refresh_token_cls.jwt_secret_key = current_app.config.get('JWT_SECRET_KEY')
        self.refresh_token_cls.jwt_exp_claim = current_app.config.get('JWT_EXP_CLAIM')
        self.refresh_token_cls.jwt_jti_claim = current_app.config.get('JWT_JTI_CLAIM')
        self.refresh_token_cls.jwt_identity_claim = current_app.config.get('JWT_IDENTITY_CLAIM')
        self.refresh_token_cls.lifetime = current_app.config.get('JWT_REFRESH_TOKEN_LIFETIME')

    def _jwt_error_callback(self, error):
        return self.jwt_error_callback(error)
