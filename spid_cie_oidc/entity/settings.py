import aiohttp

DEFAULT_JWE_ENC = "A256CBC-HS512"
ENCRYPTION_ENC_SUPPORTED = [
    "A128CBC-HS256",
    "A192CBC-HS384",
    "A256CBC-HS512",
    "A128GCM",
    "A192GCM",
    "A256GCM"
]

DEFAULT_JWS_ALG = "RS256"
SIGNING_ALG_VALUES_SUPPORTED = [
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512"
]

DEFAULT_JWE_ALG = "RSA-OAEP"
ENCRYPTION_ALG_VALUES_SUPPORTED = [
    "RSA-OAEP",
    "RSA-OAEP-256",
    "ECDH-ES",
    "ECDH-ES+A128KW",
    "ECDH-ES+A192KW",
    "ECDH-ES+A256KW"
]

DEFAULT_HASH_FUNC = "SHA-256"

# This is required in general project settings
# OIDCFED_FEDERATION_TRUST_ANCHORS = [https://..., ]

OIDCFED_ALLOWED_TRUST_MARKS = []
OIDCFED_FILTER_BY_TRUST_MARKS = True

# the metadata discovery will only processes the first MAXIMUM_AUTHORITY_HINTS
OIDCFED_MAXIMUM_AUTHORITY_HINTS = 2
OIDCFED_MAX_PATH_LEN = 1

# old, for requests
# HTTPC_PARAMS = {
    # "verify": True,
    # "timeout": 4
# }

# for aiohttp
HTTPC_PARAMS = {
    "connection": {"ssl": True},
    "session" : {"timeout": aiohttp.ClientTimeout(total=4)}
}

FEDERATION_DEFAUL_EXP = 2880
