from common.exception import APIException, Error
from app.models.account import Account, Profile
from common.extensions import db
from flask_jwt_extended.config import config


class UserProfile:
    def __init__(self, profile: Profile, account: Account):

        self.instance = profile
        self.account = account

        self.id = profile.id
        self.username = profile.username
        self.account_id = profile.account_id


class User:
    def __init__(self, account: Account, profile: Profile = None):
        self.instance = account

        self.id = account.id
        self.salt = account.salt
        self.password = account.password
        self.country_code = account.country_code
        self.phone_number = account.phone_number
        self.email = account.email

        if profile is None:
            profile = db.session.query(Profile).filter(Profile.account_id == self.id).first()

        if profile is None:
            raise
        self.profile = UserProfile(profile=profile, account=self.instance)


def expired_token_callback(_expired_jwt_header, _expired_jwt_data):
    raise APIException(error=Error.TokenExpiredError)


def invalid_token_callback(error_string):
    raise APIException(error=Error.InvalidTokenError, detail=error_string)


def user_lookup_callback(jwt_header: dict, jwt_data: dict):
    identity = jwt_data[config.identity_claim_key]

    account = db.session.query(Account).filter(Account.id == identity).first()

    return account


def verify_jwt_in_request(optional=False, fresh=False, refresh=False, locations=None):
    """
    Verify that a valid JWT is present in the request, unless ``optional=True`` in
    which case no JWT is also considered valid.

    :param optional:
        If ``True``, do not raise an error if no JWT is present in the request.
        Defaults to ``False``.

    :param fresh:
        If ``True``, require a JWT marked as ``fresh`` in order to be verified.
        Defaults to ``False``.

    :param refresh:
        If ``True``, require a refresh JWT to be verified.

    :param locations:
        A location or list of locations to look for the JWT in this request, for
        example ``'headers'`` or ``['headers', 'cookies']``. Defaults to ``None``
        which indicates that JWTs will be looked for in the locations defined by the
        ``JWT_TOKEN_LOCATION`` configuration option.
    """
    from flask import request
    from flask_jwt_extended.view_decorators import _decode_jwt_from_request
    from flask.globals import _request_ctx_stack
    from flask_jwt_extended.view_decorators import _load_user

    if request.method in config.exempt_methods:
        return

    from flask_jwt_extended.exceptions import NoAuthorizationError
    try:
        if refresh:
            jwt_data, jwt_header, jwt_location = _decode_jwt_from_request(
                locations, fresh, refresh=True
            )
        else:
            jwt_data, jwt_header, jwt_location = _decode_jwt_from_request(
                locations, fresh
            )
    except NoAuthorizationError:
        if not optional:
            raise
        _request_ctx_stack.top.jwt = {}
        _request_ctx_stack.top.jwt_header = {}
        _request_ctx_stack.top.jwt_user = {"loaded_user": None}
        _request_ctx_stack.top.jwt_location = None
        return

    # Save these at the very end so that they are only saved in the requet
    # context if the token is valid and all callbacks succeed

    _request_ctx_stack.top.jwt_user = _load_user(jwt_header, jwt_data)
    _request_ctx_stack.top.jwt_header = jwt_header
    _request_ctx_stack.top.jwt = jwt_data
    _request_ctx_stack.top.jwt_location = jwt_location

    return jwt_header, jwt_data
