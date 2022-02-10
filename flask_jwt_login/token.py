import uuid

import jwt

from flask_jwt_login import utils
from flask_jwt_login.exception import JWTError


class Token:
    token_type = None
    lifetime = None
    jwt_secret_key = None
    jwt_algorithm = None
    jwt_exp_claim = None
    jwt_jti_claim = None
    jwt_identity_claim = None

    def __init__(self, token=None):
        self.token = token
        self.current_time = utils.int_timestamp()
        if self.token:
            self.payload = self.decode_token()
        else:
            self.payload = {
                'token_type': self.token_type,
                self.jwt_jti_claim: uuid.uuid4().hex
            }

        self.set_exp()

    def set_exp(self, from_time=None, lifetime=None):
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[self.jwt_exp_claim] = from_time + lifetime

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def __delitem__(self, key):
        del self.payload[key]

    def __contains__(self, key):
        return key in self.payload

    def __str__(self):
        return self.encode_token()

    @classmethod
    def for_user(cls, user: str):
        identity = getattr(user, cls.jwt_identity_claim)

        token = cls()
        token[cls.jwt_identity_claim] = identity

        return token

    def check_exp(self):
        claim_time = self.payload[self.jwt_exp_claim]

        if claim_time < self.current_time:
            return False

        return True

    def encode_token(self):
        return jwt.encode(payload=self.payload, key=self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def decode_token(self):
        try:
            return jwt.decode(self.token, self.jwt_secret_key, algorithms=[self.jwt_algorithm, ])
        except jwt.InvalidSignatureError:
            raise JWTError("InvalidSignatureError", "invalid signature")
        except jwt.ExpiredSignatureError:
            raise JWTError("ExpiredSignatureError", "expire signature")
        except Exception as e:
            raise JWTError("UnknownError", "unknown signature")


class AccessToken(Token):
    token_type = 'access'


class RefreshToken(Token):
    token_type = 'refresh'

    @property
    def access_token(self):
        access = AccessToken()
        access[access.jwt_identity_claim] = self.payload[self.jwt_identity_claim]
        return access

