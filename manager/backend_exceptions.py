class ProxyManagerBackendException(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(args, kwargs)

    def __str__(self):
        return self.msg


class UnverifiedAccountError(ProxyManagerBackendException):
    pass


class InvalidTokenError(ProxyManagerBackendException):
    pass
