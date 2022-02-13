from functools import wraps

from flask import (_request_ctx_stack, current_app, has_request_context)
from werkzeug.local import LocalProxy

from flask_jwt_login.constants import EXTENSION_KEY

current_identity = LocalProxy(lambda : load_current_user)
_jwt = LocalProxy(lambda: current_app.extensions[EXTENSION_KEY])


def load_current_user():
    if has_request_context() and not hasattr(_request_ctx_stack.top, 'user'):
        current_app.extensions['jwt-login']._load_identity()

    return getattr(_request_ctx_stack.top, 'user', None)


def jwt_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_identity is None:
            return _jwt.unauthorized_callback()
        return func(*args, **kwargs)
    return decorated_view





