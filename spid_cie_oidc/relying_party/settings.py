from django.conf import settings
from spid_cie_oidc.provider.schemas.authn_requests import AcrValues, AuthenticationRequestCie, AuthenticationRequestDoc, AuthenticationRequestSpid
from spid_cie_oidc.entity.schemas.rp_metadata import RPMetadataSpid, RPMetadataCie
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationResponse, AuthenticationResponseCie
from spid_cie_oidc.provider.schemas.token_response import TokenResponse


RP_PREFS = {
    "application_name": "that_fancy_rp",
    "application_type": "web",
    "contacts": ["ops@example.com"],
    "response_types": ["code"],
    "scope": ["openid", "offline_access"],
    "token_endpoint_auth_method": ["private_key_jwt"],
}


OIDCFED_ACR_PROFILES = getattr(
    settings,
    "OIDCFED_ACR_PROFILES",
    AcrValues.l2.value
)

RP_PROVIDER_PROFILES = getattr(
    settings,
    "RP_PROVIDER_PROFILES",
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
            "authorization_request_doc": AuthenticationRequestDoc,
            "rp_metadata": RPMetadataSpid,
            "authn_response": AuthenticationResponse,
            "token_response": TokenResponse
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
            "authorization_request_doc": AuthenticationRequestDoc,
            "rp_metadata": RPMetadataCie,
            "authn_response": AuthenticationResponseCie,
            "token_response": TokenResponse
        },
    },
)

RP_USER_LOOKUP_FIELD = getattr(settings, "RP_USER_LOOKUP_FIELD", "fiscal_number")
RP_USER_CREATE = getattr(settings, "RP_USER_CREATE", True)

RP_ATTR_MAP = getattr(
    settings,
    "RP_ATTR_MAP",
    {
        "sub": ("sub",),
        "username": (
            {
                "func": "spid_cie_oidc.relying_party.processors.issuer_prefixed_sub",
                "kwargs": {"sep": "__"},
            },
        ),
        "first_name": ("given_name", "https://attributes.spid.gov.it/name"),
        "last_name": (
            "family_name",
            "https://attributes.spid.gov.it/familyName",
        ),
        "email": (
            "email",
            "https://attributes.spid.gov.it/email",
        ),
        "fiscal_number": ("https://attributes.spid.gov.it/fiscalNumber", "fiscal_number"),
    },
)


SPID_REQUESTED_CLAIMS = getattr(
    settings,
    "RP_REQUIRED_CLAIMS",
    {
        "id_token": {
            "https://attributes.spid.gov.it/familyName": {"essential": True},
            "https://attributes.spid.gov.it/email": {"essential": True},
        },
        "userinfo": {
            "https://attributes.spid.gov.it/name": None,
            "https://attributes.spid.gov.it/familyName": None,
            "https://attributes.spid.gov.it/email": None,
            "https://attributes.spid.gov.it/fiscalNumber": None,
        },
    },
)

CIE_REQUESTED_CLAIMS = getattr(
    settings,
    "RP_REQUIRED_CLAIMS",
    {
        "id_token": {"family_name": {"essential": True}, "email": {"essential": True}},
        "userinfo": {
            "given_name": None,
            "family_name": None,
            "email": None,
            "fiscal_number": None
        },
    },
)

RP_PKCE_CONF = getattr(
    settings,
    "RP_PKCE_CONF",
    {
        "function": "spid_cie_oidc.relying_party.utils.get_pkce",
        "kwargs": {"code_challenge_length": 64, "code_challenge_method": "S256"},
    },
)

RP_REQUEST_CLAIM_BY_PROFILE = {
    "spid": SPID_REQUESTED_CLAIMS,
    "cie": CIE_REQUESTED_CLAIMS,
}

RP_DEFAULT_PROVIDER_PROFILES = getattr(settings, "RP_DEFAULT_PROVIDER_PROFILES", "spid")
RP_REQUEST_EXP = getattr(settings, "RP_REQUEST_EXP", 60)
