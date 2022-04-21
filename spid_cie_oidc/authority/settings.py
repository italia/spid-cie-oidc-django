from django.conf import settings
from spid_cie_oidc.entity import settings as entity_settings

MAX_ENTRIES_PAGE = getattr(settings, "MAX_ENTRIES_PAGE", 100)
DEFAULT_JWS_ALG = getattr(settings, "DEFAULT_JWS_ALG", entity_settings.DEFAULT_JWS_ALG)
DEFAULT_JWE_ALG = getattr(settings, "DEFAULT_JWE_ALG", entity_settings.DEFAULT_JWE_ALG)
DEFAULT_JWE_ENC = getattr(settings, "DEFAULT_JWE_ENC", entity_settings.DEFAULT_JWE_ENC)
SIGNING_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "SIGNING_ALG_VALUES_SUPPORTED",
    entity_settings.SIGNING_ALG_VALUES_SUPPORTED,
)
ENCRYPTION_ALG_VALUES_SUPPORTED = getattr(
    settings,
    "ENCRYPTION_ALG_VALUES_SUPPORTED",
    entity_settings.ENCRYPTION_ALG_VALUES_SUPPORTED,
)
ENCRYPTION_ENC_SUPPORTED = getattr(
    settings, "ENCRYPTION_ENC_SUPPORTED", entity_settings.ENCRYPTION_ENC_SUPPORTED
)

FEDERATION_DEFAULT_POLICY = getattr(
    settings, "FEDERATION_DEFAULT_POLICY", {
        "openid_provider": {
            "subject_types_supported": {"value": ["pairwise"]},
            "id_token_signing_alg_values_supported": {
                "subset_of": SIGNING_ALG_VALUES_SUPPORTED
            },
            "userinfo_signing_alg_values_supported": {
                "subset_of": SIGNING_ALG_VALUES_SUPPORTED
            },
            "token_endpoint_auth_methods_supported": {"value": ["private_key_jwt"]},
            "userinfo_encryption_alg_values_supported": {
                "subset_of": ENCRYPTION_ALG_VALUES_SUPPORTED
            },
            "userinfo_encryption_enc_values_supported": {
                "subset_of": ENCRYPTION_ENC_SUPPORTED
            },
            "request_object_encryption_alg_values_supported": {
                "subset_of": ENCRYPTION_ALG_VALUES_SUPPORTED
            },
            "request_object_encryption_enc_values_supported": {
                "subset_of": ENCRYPTION_ENC_SUPPORTED
            },
            "request_object_signing_alg_values_supported": {
                "subset_of": SIGNING_ALG_VALUES_SUPPORTED
            },
        },
        "openid_relying_party": {
            "grant_types": {"subset_of": ["authorization_code", "refresh_token"]},
            "scope": {
                "superset_of": ["openid"],
                "subset_of": ["openid", "offline_access"],
            },
        },
        "federation_entity": {},
        "oauth_resource": {},
    }
)
