import json
from typing import Optional, Tuple

from flask import request
from werkzeug.exceptions import HTTPException


class Error:
    # 基础错误
    NotDefinedError = (100001, '服务器开小差了,请稍后再试')
    NotFoundError = (100002, '无效页')
    PermissionError = (100003, '您没有权限，如有疑问请联系管理员')
    NotAuthenticatedError = (100004, '请登录')
    DBError = (100005, '服务器开小差了,请稍后再试')
    RequestThrottledError = (100006, '请求速度过快,请稍后再试')
    AuthError = (100007, '账号或密码错误')
    InvalidParamsError = (100008, '无效的请求参数')
    TooManyDataError = (100009, '查询到太多的数据,请添加查询条件')
    ObjectNotFountError = (100010, '没有找到这条记录')
    TokenExpireError = (100011, '页面已过期,请刷新重试')
    NetWorkError = (100014, '服务器开小差了,请稍后再试')


class APIException(HTTPException):
    code = 200
    detail = 'sorry, we made a mistake!'
    error_code = 'A0000'

    def __init__(
            self, detail=None, error_code: Optional[str] = None, error: Optional[Tuple[str, str]] = None,
            extra_info=None
    ):
        if detail:
            self.detail = detail
        if error_code:
            self.error_code = error_code
        if error:
            self.error_code = error[0]
            self.detail = error[1]
        self.extra_info = extra_info

        super(APIException, self).__init__(detail, None)

    def get_body(self, environ=None, scope=None):
        body = dict(
            detail=self.detail,
            code=self.error_code,
            success=False,
            data=None,
            extra_info=self.extra_info,
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None, scope=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
