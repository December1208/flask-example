from flask_jwt_login import utils


class Token:
    token_type = None
    lifetime = None
    jwt_secret_key = None
    jwt_algorithm = None
    not_before_delta = None

    def __init__(self, token=None):
        self.token = token

    def get_payload(self, user):
        iat = utils.int_timestamp()
        exp = iat + self.lifetime
        nbf = iat + self.not_before_delta
        user_id = getattr(user, "id") or user['id']
        payload = {
            "iat": iat,
            "exp": exp,
            "nbf": nbf,
            "user_id": user_id,
            "token_type": self.token_type,
            "jti": utils.uuid4_str()
        }
        return payload


class AccessToken(Token):
    token_type = 'access'


class RefreshToken(Token):
    token_type = 'refresh'

