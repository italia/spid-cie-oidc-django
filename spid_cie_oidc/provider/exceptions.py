class AuthzRequestReplay(Exception):
    pass


class InvalidSession(Exception):
    pass


class RevokedSession(Exception):
    pass


class ValidationException(Exception):
    pass


class ExpiredAuthCode(Exception):
    pass


class InvalidRefreshRequestException(Exception):
    pass
