from django.conf import settings


RP_PREFS = {
    "application_name": "that_fancy_rp",
    "application_type": "web",
    "contacts": ["ops@example.com"],
    "response_types": ["code"],
    "scope": ["openid", "offline_access"],
    "token_endpoint_auth_method": ["private_key_jwt"],
}


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
        "kwargs": {"code_challenge_length": 64, "code_challenge_method": "S256"},
    }
)    
