DEFAULT_JWE_ALG = "RSA-OAEP"
DEFAULT_JWE_ENC = "A256CBC-HS512"
DEFAULT_JWS_ALG = "RS256"
DISABLED_JWT_ALGS = ("RSA_1_5", "none")
DEFAULT_HASH_FUNC = "SHA-256"

# This is required in general project settings
# FEDERATION_TRUST_ANCHOR = https://...

FEDERATION_WELLKNOWN_URL = ".well-known/openid-federation"
MAX_DISCOVERY_REQUESTS = 5
HTTPC_PARAMS = {
    "verify": True,
    "timeout": 4
}
