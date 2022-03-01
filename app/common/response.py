from flask import jsonify
from typing import Dict, Union, List


def _build_response_data(data=None, page_info=None):
    if page_info:
        result = {
            'result': data,
            'next': page_info['next'],
            'previous': page_info['previous'],
            'count': page_info['count']
        }
    else:
        result = data

    return result


def standard_response(data: Union[List, Dict] = None, page_info: Dict = None):
    response_data = {
        'code': 200,
        'data': _build_response_data(data, page_info),
        'success': True,
        'detail': ''
    }

    return jsonify(response_data), 200
