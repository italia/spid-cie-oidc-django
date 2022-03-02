from django.conf import settings
from spid_cie_oidc.onboarding.schemas.authn_requests import (
    AcrValuesCie,
    AcrValuesSpid
)


RP_PREFS = {
    "application_name": "that_fancy_rp",
    "application_type": "web",
    "contacts": ["ops@example.com"],
    "response_types": ["code"],
    "scope": ["openid", "offline_access"],
    "token_endpoint_auth_method": ["private_key_jwt"],
}


RP_PROVIDER_PROFILES = getattr(
    settings,
    'RP_PROVIDER_PROFILES',
    {
        "spid": {
            "authorization_request": {
                "acr_values": AcrValuesSpid.l2.value
            },
        },
        "cie": {
            "authorization_request": {
                "acr_values": AcrValuesCie.l2.value
            },
        }
    }
)


RP_ATTR_MAP = {
    "username": (
        {
            "func": "spid_cie_oidc.relying_party.processors.issuer_prefixed_sub",
            "kwargs": {"sep": "__"},
        },
    ),
    "first_name": ("firstname",),
    "last_name": ("lastname",),
    "email": ("email",),
}


RP_PKCE_CONF = getattr(
    settings,
    "RP_PKCE_CONF",
    {
        "function": "spid_cie_oidc.relying_party.utils.get_pkce",
        "kwargs": {
            "code_challenge_length": 64,
            "code_challenge_method": "S256"
        },
    }
)
