from django.core.exceptions import ValidationError

class HttpError(Exception):
    pass


class TrustChainHttpError(HttpError):
    pass


class UnknownKid(Exception):
    pass


class MissingAuthorityHintsClaim(ValidationError):
    pass


class NotDescendant(ValidationError):
    pass
