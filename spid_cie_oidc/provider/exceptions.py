class AuthzRequestReplay(Exception):
    pass


class InvalidSession(Exception):
    pass


class RevokedSession(Exception):
    pass


class ValidationException(Exception):
    pass
