from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.common import response
from app.settings import setting

account_api = Blueprint('account-api', __name__)


@account_api.route('/account/login/', methods=['POST'])
def _login():

    req_data = request.get_json() or {}

    account = req_data.get('account')
    password = req_data.get('password')

    if account != "123" or password != "123":
        raise

    result = {
        "access_token": create_access_token(identity=1),
        "refresh_token": create_refresh_token(identity=1),
        "lifetime": setting.JWT_ACCESS_TOKEN_EXPIRES
    }

    return response.standard_response(result)


@account_api.route('/account/refresh/', methods=['POST'])
@jwt_required(refresh=True, locations=['json'])
def _refresh():

    identity = get_jwt_identity()
    result = {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "lifetime": setting.JWT_ACCESS_TOKEN_EXPIRES
    }
    return response.standard_response(result)


@account_api.route('/account/profile/', methods=['GET'])
@jwt_required()
def _profile():
    return response.standard_response({})
