from flask_jwt_login import utils


class Token:
    token_type = None
    lifetime = None
    jwt_secret_key = None
    jwt_algorithm = None
    jwt_exp_claim = None
    jwt_jti_claim = None
    jwt_identity_claim = None
    not_before_delta = None

    def __init__(self, token=None):
        self.token = token

    def get_payload(self, identity):
        iat = utils.int_timestamp()
        exp = iat + self.lifetime
        nbf = iat + self.not_before_delta
        identity_value = getattr(identity, self.jwt_identity_claim) or identity[self.jwt_identity_claim]
        payload = {
            "iat": iat,
            "exp": exp,
            "nbf": nbf,
            self.jwt_identity_claim: identity_value,
            "token_type": self.token_type
        }
        return payload


class AccessToken(Token):
    token_type = 'access'


class RefreshToken(Token):
    token_type = 'refresh'

