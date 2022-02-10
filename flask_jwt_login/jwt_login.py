from collections import OrderedDict

import jwt
from flask import current_app, request, Flask, jsonify
from werkzeug.local import LocalProxy
from flask_jwt_login import utils
from flask_jwt_login.exception import JWTError
from flask_jwt_login.token import RefreshToken, AccessToken

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


def _default_access_jwt_payload_handler(identity):
    iat = utils.int_timestamp()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    identity_claim = current_app.config.get('JWT_IDENTITY_CLAIM')
    identity_value = getattr(identity, identity_claim) or identity[identity_claim]
    return {'exp': exp, 'iat': iat, 'nbf': nbf, identity_claim: identity_value, 'token_type': TokenType.ACCESS}


def _default_refresh_jwt_payload_handler(identity):
    iat = utils.int_timestamp()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    identity_claim = current_app.config.get('JWT_IDENTITY_CLAIM')
    identity_value = getattr(identity, identity_claim) or identity[identity_claim]
    return {'exp': exp, 'iat': iat, 'nbf': nbf, identity_claim: identity_value, 'token_type': TokenType.REFRESH}


def _default_jwt_payload_handler(identity, token_type=TokenType.ACCESS):
    if token_type == TokenType.ACCESS:
        payload = _jwt.access_jwt_payload_callback(identity)
    elif token_type == TokenType.REFRESH:
        payload = _jwt.refresh_jwt_payload_callback(identity)
    else:
        raise JWTError("Unknown Token Type", "unknown token type", 400)
    return payload


def _default_jwt_decode_handler(token):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']

    return jwt.decode(token, secret, algorithms=[algorithm])


def _default_jwt_encode_handler(identity):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    payload = _jwt.jwt_payload_callback(identity)

    return jwt.encode(payload, secret, algorithm=algorithm)


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

        self.jwt_payload_callback = None
        self.access_jwt_payload_callback = None
        self.refresh_jwt_payload_callback = None
        self.jwt_encode_callback = None
        self.jwt_decode_callback = None
        self.jwt_error_callback = None
        self.request_handler = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.errorhandler(JWTError)(self._jwt_error_callback)
        self.init_access_token_cls()
        self.init_refresh_token_cls()

    def init_access_token_cls(self):
        self.access_token_cls.jwt_algorithm =
        pass

    def init_refresh_token_cls(self):
        pass

    def _jwt_error_callback(self, error):
        return self.jwt_error_callback(error)

    def get_refresh_token(self, identity):
        return self.jwt_encode_callback(identity)

    def get_access_token(self, identity):
        return self.jwt_encode_callback(identity)
