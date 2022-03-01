from app.common.exception import APIException, Error


def expired_token_callback(_expired_jwt_header, _expired_jwt_data):
    raise APIException(error=Error.TokenExpiredError)


def invalid_token_callback(error_string):
    raise APIException(error=Error.InvalidTokenError, detail=error_string)
