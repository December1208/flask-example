
import json

import requests
from requests import Response
from requests.exceptions import ReadTimeout, ConnectTimeout

from common.extensions import logger
from utils import time as time_util


class NetWorkError(Exception):
    pass


class V2BusinessException(Exception):
    def __init__(self, response: Response, code, msg):
        self.response = response
        self.code = code
        self.msg = msg


def check_and_raise_http_exception(response: Response):
    if response.status_code // 10 == 20:
        return

    error_msg = 'Request Exception:{}\n'.format(' status code is {}'.format(response.status_code))
    logger.error(f"{error_msg}, content: {response.content}")
    raise NetWorkError


def check_and_raise_business_exception(response: Response):
    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        logger.error(f'the response content: {response.content}')
        raise NetWorkError
    except Exception as e:
        logger.error(f'get response json error, detail: {type(e)}, {e.args}, {response.content}')
        raise NetWorkError
    else:
        if response_data['code'] == 200:
            return
        logger.error(f'response api code != 200, detail: {response_data}')
        raise V2BusinessException(response=response, code=response_data['code'], msg=response_data['detail'])


@time_util.timer
def request_twice_if_fail(
    url, params=None, header=None, json=None, files=None, cookies=None, method='get', read_timeout=3,
):

    request_dict = {
        'get': requests.get,
        'post': requests.post,
        'delete': requests.delete,
        'put': requests.put,
        'patch': requests.patch
    }
    # 确保发送完成, 发送请求两次
    logger.info(f'first req, url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}')
    try:
        response = request_dict[method](url=url, headers=header, params=params, json=json, files=files, cookies=cookies,
                                        timeout=(2, read_timeout))
    except(ReadTimeout, ConnectTimeout, ConnectionError, Exception):
        logger.warning(f'second req, url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}')
        response = request_dict[method](url=url, headers=header, params=params, json=json, files=files, cookies=cookies,
                                        timeout=(2, read_timeout + 2))

    check_and_raise_http_exception(response)
    check_and_raise_business_exception(response)
    return response
