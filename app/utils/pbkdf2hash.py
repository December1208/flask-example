import base64
import hashlib

from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

from app.utils.helper import get_random_string


class PBKDF2PasswordHash:
    algorithm = "pbkdf2_sha256"
    iterations = 150000
    digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        _hash = PBKDF2(password, salt, dkLen=32, count=iterations, hmac_hash_module=SHA256)
        _hash = base64.b64encode(_hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, _hash)

    def verify(self, password, encoded):
        if not encoded:
            return False
        algorithm, iterations, salt, _hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return encoded == encoded_2

    @staticmethod
    def salt():
        return get_random_string()


pbkdf2_password_hash = PBKDF2PasswordHash()
