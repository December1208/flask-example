
import json

import requests
from requests import Response
from requests.exceptions import ReadTimeout, ConnectTimeout
from app.extensions import logger
from app.utils import time as custom_time
from app.common.exception import Error, APIException


class NetWorkError(Exception):
    pass


def check_http_success(response: Response):
    if response.status_code // 10 != 20:
        error_msg = 'Request Exception:{}\n'.format(' status code is {}'.format(response.status_code))
        logger.warning(error_msg)
        return False
    return True


def _request_twice_if_fail(url, params=None, header=None, json=None, files=None, cookies=None, method='get'):
    def raise_request_detail():
        logger.warning(
            f'url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}, cookies: {cookies}')
        logger.warning(f'response text: {response.text}')
        raise NetWorkError

    request_dict = {
        'get': requests.get,
        'post': requests.post,
        'delete': requests.delete,
        'put': requests.put
    }
    # 确保发送完成, 发送请求两次
    logger.info(f'try to request {method.upper()} : {url}')
    try:
        response = request_dict[method](url=url, headers=header, params=params, json=json, files=files, cookies=cookies,
                                        timeout=(2, 3))
    except(ReadTimeout, ConnectTimeout, ConnectionError, Exception):
        logger.warning(f'url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}')
        response = request_dict[method](url=url, headers=header, params=params, json=json, files=files, cookies=cookies,
                                        timeout=(2, 5))

    # 根据约定判断请求是否成功
    if 'v2' in url and not check_v2_api_success(response):
        raise_request_detail()
    elif not check_http_success(response):
        raise_request_detail()

    return response


def check_v2_api_success(response: Response):
    if not check_http_success(response):
        return False

    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        logger.warning(f'the response content: {response.content}')
        return False
    except Exception as e:
        logger.warning(f'get response json error, detail: {type(e)}, {e.args}, {response.content}')
        return False
    else:
        if response_data['code'] != 200:
            logger.warning(f'response api code != 200, detail: {response_data}')
            return False

    return True


@custom_time.timer
def request_twice_if_fail(url, params=None, header=None, json=None, files=None, cookies=None, method='get'):
    try:
        response = _request_twice_if_fail(url, params, header, json, files, cookies, method)

    except NetWorkError as e:
        raise APIException(error=Error.NetWorkError)

    return response
