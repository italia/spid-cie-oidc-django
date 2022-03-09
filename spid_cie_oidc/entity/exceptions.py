from django.core.exceptions import ValidationError


class HttpError(Exception):
    pass


class TrustChainHttpError(HttpError):
    pass


class UnknownKid(Exception):
    pass


class MissingJwksClaim(ValidationError):
    pass


class MissingAuthorityHintsClaim(ValidationError):
    pass


class NotDescendant(ValidationError):
    pass


class TrustAnchorNeeded(ValidationError):
    pass


class MetadataDiscoveryException(ValidationError):
    pass


class MissingTrustMark(ValidationError):
    pass


class InvalidRequiredTrustMark(ValidationError):
    pass


class InvalidTrustchain(ValidationError):
    pass


class TrustchainMissingMetadata(ValidationError):
    pass


class InvalidEntityConfiguration(ValidationError):
    pass
