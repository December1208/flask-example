import pathlib
import time

import oss2

from apps.foundation import logger
from apps.settings import setting

OSS_UPLOAD_MAX_RETRIES = 2


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class OSSUtil(metaclass=SingletonMeta):
    def __init__(self):
        auth = oss2.Auth(setting.OSS_ACCESS_KEY_ID,
                         setting.OSS_SECRET_ACCESS_KEY)
        self.bucket = oss2.Bucket(auth, 'http://' + setting.OSS_ENDPOINT, setting.OSS_BUCKET_NAME)

    def upload(self, filename, data, prefix='', public=True, headers=None):
        key = prefix + filename
        result = self.bucket.put_object(key, data, headers=headers)
        if result.status == 200:
            logger.info(f'upload file success, key: {key}')
            return True
        else:
            logger.warning("upload file failed: " + key)
            for i in range(OSS_UPLOAD_MAX_RETRIES):
                time.sleep(1)
                result = self.bucket.put_object(key, data, headers=headers)
                if result.status == 200:
                    logger.info(f"after retrying {i + 1} times, succeed in uploading file, key: {key}")
                    break
            else:
                logger.error("after retrying 3 times, fail to upload file, key: {}".format(key))
        if public:
            self.bucket.put_object_acl(key, oss2.OBJECT_ACL_PUBLIC_READ)
        return False

    def download(self, key, binary=False):
        result = self.bucket.get_object(key)
        if binary:
            return result.read()
        else:
            return result.read().decode('utf-8')

    def list(self, prefix, no_folder=True, list_sub_folders=False):
        result = self.bucket.list_objects(prefix)
        if result.status != 200:
            return []

        files = []
        files.extend(result.object_list)
        while result.next_marker:
            next_marker = result.next_marker
            result = self.bucket.list_objects(prefix, marker=next_marker)
            files.extend(result.object_list)

        key_list = list(map(lambda x: x.key, files))
        if no_folder:
            key_list = list(filter(lambda x: not x.endswith('/'), key_list))
        elif not list_sub_folders:
            folders_set = set(filter(lambda x: x.endswith('/'), key_list))
            folders_set_to_remove = set()
            for key in key_list:
                if key in folders_set:
                    continue
                sub_folders_set = set()
                path_parts = pathlib.Path(key).parts
                for i in range(1, len(path_parts)):
                    sub_folders_set.add('/'.join(path_parts[:i]) + '/')
                folders_set_to_remove |= (folders_set & sub_folders_set)

            key_list = list(set(key_list) - set(folders_set_to_remove))
        return key_list
