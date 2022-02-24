import os
from tempfile import NamedTemporaryFile
from typing import List

from apps.common.exception import APIException, Error
from apps.settings import setting
from apps.utils.request import request_twice_if_fail
from apps.foundation import logger, db
from apps.utils import helper

"""
file_field: 
{
    "identity": "xxx.png",
    "pri_type": FileAttrType.PUBLIC,
    "domain": "storage-test1.lintcode.com"
}
"""


class FileAttrType:
    PUBLIC = 1  # 公有
    PRIVATE = 2  # 私有


GET_PUBLIC_FILE_ENDPOINT = setting.STORAGE_HOST.rstrip('/') + '/v2/inner_api/puburl'
GET_PRIVATE_FILE_ENDPOINT = setting.STORAGE_HOST.rstrip('/') + '/v2/inner_api/puburl'
UPLOAD_FILE_ENDPOINT = setting.STORAGE_HOST.rstrip('/') + '/v2/inner_api/upload/'


class StorageFile:
    def __init__(self, identity, pri_type, domain, pub_url=None, name=None, file_type=None):
        self.identity = identity
        self.pri_type = pri_type
        self.domain = domain
        self.pub_url = pub_url
        self.name = name
        self.file_type = file_type

    def to_json(self, detail=False):
        result = {
            'identity': self.identity,
            'pri_type': self.pri_type,
            'domain': self.domain,
            'name': self.name,
            'type': self.file_type
        }
        if detail:
            result.update({
                'url': self.pub_url
            })
        return result

    @classmethod
    def init_from_json(cls, data):
        return cls(
            identity=data['identity'],
            pri_type=data['pri_type'],
            domain=data['domain'],
            pub_url=data.get('url'),
            name=data.get('name'),
            file_type=data.get('type')
        )


class LocalFile:
    PREFIX = 'tmp/backend/'

    def __init__(self, file_name=None, path=None, url=None, content=None, oss_prefix=PREFIX):
        self.path = path
        self.url = url
        self.file_name = file_name
        self.content = content
        self.oss_prefix = oss_prefix
        if content is not None and file_name is None:
            raise Exception("使用content时，file_name是必填项")

        if path:
            self.content = self._read_content_from_path()
            self.file_name = helper.uuid() + f'.{os.path.splitext(path)[-1]}'
        elif url:
            self.content, suffix = self._read_content_from_url()
            self.file_name = helper.uuid_str() + f".{suffix}"

        self.oss_uri = f"{self.oss_prefix}{self.file_name}"

    def upload2oss(self):
        if self.content is None:
            data = []
        else:
            data = upload_data_to_storage(self.oss_uri, self.content)
        return data

    def _read_content_from_path(self):
        with open(self.path, 'rb') as f:
            content = f.read()

        return content

    def _read_content_from_url(self):
        try:
            response = request_twice_if_fail(
                url=self.url,
                method='get'
            )
        except APIException as e:
            logger.error(f"[GET FILE CONTENT FROM URL ERROR], url: {self.url}")
            return None, ''

        return helper.get_content_and_type(response)


def _get_public_file_list(file_field_list):
    data = [{'ident': i['identity'], 'domain': i['domain']} for i in file_field_list]
    logger.info(f'[_get_public_file_list] request body: {data}')
    response = request_twice_if_fail(
        url=GET_PUBLIC_FILE_ENDPOINT,
        json=data,
        method='post'
    )
    logger.info(f'[_get_public_file_list] response body: {response.json()}')
    response_data = response.json()['data']
    return response_data


def _get_private_file_list(file_field_list):
    data = [{'ident': i['identity'], 'domain': i['domain']} for i in file_field_list]
    logger.info(f'[_get_private_file_list] request body: {data}')
    response = request_twice_if_fail(
        url=GET_PRIVATE_FILE_ENDPOINT,
        json=data,
        method='post'
    )
    logger.info(f'[_get_private_file_list] response body: {response.json()}')
    response_data = response.json()['data']
    return response_data


def bulk_set_pub_url_for_storage_file_list(storage_file_list: List[StorageFile]):
    if not setting.REQUEST_STORAGE:
        return

    public_file_field_list = []
    private_file_field_list = []
    identity_to_storage_file = {sf.identity: sf for sf in storage_file_list}
    for storage_file in storage_file_list:
        if storage_file.pri_type == FileAttrType.PUBLIC:
            public_file_field_list.append(storage_file.to_json())
        elif storage_file.pri_type == FileAttrType.PRIVATE:
            private_file_field_list.append(storage_file.to_json())
        else:
            logger.error(f'unknown storage file pri_type. {storage_file.pri_type}')
    public_file_list = []
    private_file_list = []
    if public_file_field_list:
        public_file_list = _get_public_file_list(public_file_field_list)
    if private_file_field_list:
        private_file_list = _get_private_file_list(private_file_field_list)
    for file_data in public_file_list + private_file_list:
        pub_url = file_data['pub_url']
        ident = file_data['ident']
        _storage_file = identity_to_storage_file.get(ident)
        if _storage_file:
            _storage_file.pub_url = pub_url


def upload_data_to_storage(filename, file_data):
    logger.info(f'[upload_data_to_storage] filename: {filename}')
    files = {
        'file': (filename, file_data)
    }
    response = request_twice_if_fail(
        url=UPLOAD_FILE_ENDPOINT,
        method='post',
        files=files,
    )
    logger.info(f'[upload_data_to_storage] response_content: {response.content}')
    data = response.json()['data']
    return data


def download_data_from_storage(oss_uri):
    response = request_twice_if_fail(
        url=oss_uri,
        method='get'
    )
    return response


def init_file_data(file_data: list) -> List[StorageFile]:
    try:
        storage_file = [StorageFile.init_from_json(item) for item in file_data]
    except KeyError as exc:
        logger.warning(f'init file data error. exc: {exc}. file data: {file_data}')
        raise APIException(error=Error.InvalidParamsError)
    return storage_file


def attach_storage_file(target_list: List[dict], file_field_name='image'):
    file_data_list = [tar[file_field_name] for tar in target_list]
    storage_file_list = []
    for file_data in file_data_list:
        storage_file = init_file_data(file_data)
        storage_file_list.extend(storage_file)

    bulk_set_pub_url_for_storage_file_list(storage_file_list)
    identity_to_storage_file = {sf.identity: sf.to_json(detail=True) for sf in storage_file_list}
    for target in target_list:
        target_storage_file_list = [
            identity_to_storage_file.get(file_data['identity'])
            for file_data in target[file_field_name]
        ]
        target[file_field_name] = target_storage_file_list
    return identity_to_storage_file
