from django.conf import settings

import aiohttp


ENCRYPTION_ENC_SUPPORTED = [
    "A128CBC-HS256",
    "A192CBC-HS384",
    "A256CBC-HS512",
    "A128GCM",
    "A192GCM",
    "A256GCM",
]

DEFAULT_HASH_FUNC = "SHA-256"

DEFAULT_JWS_ALG = getattr(settings, "DEFAULT_JWS_ALG", "RS256")
DEFAULT_JWE_ALG = getattr(settings, "DEFAULT_JWE_ALG", "RSA-OAEP")
DEFAULT_JWE_ENC = getattr(settings, "DEFAULT_JWE_ENC", "A256CBC-HS512")
SIGNING_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "SIGNING_ALG_VALUES_SUPPORTED",
    ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
)
ENCRYPTION_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "ENCRYPTION_ALG_VALUES_SUPPORTED",
    [
        "RSA-OAEP",
        "RSA-OAEP-256",
        "ECDH-ES",
        "ECDH-ES+A128KW",
        "ECDH-ES+A192KW",
        "ECDH-ES+A256KW",
    ],
)

# This is required in general project settings
# OIDCFED_TRUST_ANCHORS = [https://..., ]

OIDCFED_ALLOWED_TRUST_MARKS = []
OIDCFED_FILTER_BY_TRUST_MARKS = True

# the metadata discovery will only processes the first MAXIMUM_AUTHORITY_HINTS
OIDCFED_MAX_PATH_LEN = 1

# old, for requests
# HTTPC_PARAMS = {
# "verify": True,
# "timeout": 4
# }

# for aiohttp
HTTPC_TIMEOUT = getattr(settings, "HTTPC_TIMEOUT", 12)
HTTPC_PARAMS = getattr(
    settings,
    "HTTPC_PARAMS",
    {
        "connection": {"ssl": True},
        "session": {"timeout": aiohttp.ClientTimeout(total=HTTPC_TIMEOUT)},
    },
)

# in minutes
MAX_ACCEPTED_TIMEDIFF = 5


OIDCFED_MAXIMUM_AUTHORITY_HINTS = getattr(
    settings,
    "OIDCFED_MAXIMUM_AUTHORITY_HINTS",
    2,
)

FEDERATION_DEFAULT_EXP = getattr(settings, "FEDERATION_DEFAULT_EXP", 2880)

ENTITY_TYPE_LEAFS = ["openid_relying_party", "openid_provider", "oauth_resource"]
ENTITY_TYPES = ["federation_entity"] + ENTITY_TYPE_LEAFS
ENTITY_STATUS = {
    "unreachable": False,
    "valid": True,
    "signature_failed": False,
    "not_valid": False,
    "unknown": None,
    "expired": None,
}
