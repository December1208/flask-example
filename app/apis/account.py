from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.common import response
from app.common.exception import APIException
from app.extensions import db
from app.models.account import Account
from app.settings import setting
from app.utils import pbkdf2hash, helper
from app.serializers.account import CreateAccountSerializer


account_api = Blueprint('account-api', __name__)


@account_api.route('/account/', methods=['POST'])
def _create_account():
    serializer = CreateAccountSerializer().load(request.get_json() or {})
    account = Account()

    account.email = serializer['email']
    account.salt = pbkdf2hash.pbkdf2_password_hash.salt()
    account.password = pbkdf2hash.pbkdf2_password_hash.encode(
        serializer['password'], account.salt
    )
    db.session.add(account)
    helper.safe_commit()
    return response.standard_response()


@account_api.route('/account/login/', methods=['POST'])
def _login():

    req_data = request.get_json() or {}

    email = req_data.get('email')
    password = req_data.get('password')

    account: Account = db.session.query(Account).filter(Account.email == email).first()
    if account is None or not pbkdf2hash.pbkdf2_password_hash.verify(password, account.password):
        raise APIException(detail="账号或密码错误.")

    result = {
        "access_token": create_access_token(identity=account.id),
        "refresh_token": create_refresh_token(identity=account.id),
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
