import json
import os


class Setting(object):

    default = {
        'ENV': 'development',
        'DEBUG': True,
        'TESTING': False,
        'SECRET_KEY': '6ea36d022bb44727be60ca22483fa22d999535294fd4922242b470a922e955c3',
        'API_SECRET_KEY': 'ddfaac4a33c94806',
        'SQLALCHEMY_DATABASE_URI': 'postgresql://lintcodesaas:lintcodesaas@localhost:5432/lintcode_saas',
        'TEST_SQLALCHEMY_DATABASE_URI': 'postgresql://lintcodesaas:lintcodesaas@localhost:5432/test_lintcode_saas',
    }

    def __init__(self):
        env_file_path = 'env.json'
        if not os.path.exists(env_file_path):
            raise RuntimeError(f'请在项目根目录下创建配置文件: {env_file_path}')

        with open(env_file_path, 'r') as f:
            envs: dict = json.load(f)

        for key in self.default.keys():
            value = envs.get(key, None)
            if value is None:
                value = os.environ.get(key, None)
            if value is None:
                value = self.default[key]

            value = self._convert_type(key, value)

            setattr(self, key, value)

    def _convert_type(self, k, v):
        default_value = self.default[k]
        if default_value is None:
            return v

        type_ = type(default_value)
        if type_ == bool:
            v = int(v)

        return type_(v)


setting = Setting()
