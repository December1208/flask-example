class JWTError(Exception):
    def __init__(self, error, description, status_code=401):
        self.error = error
        self.description = description
        self.status_code = status_code

    def __repr__(self):
        return 'JWTError: %s' % self.error

    def __str__(self):
        return '%s. %s' % (self.error, self.description)
