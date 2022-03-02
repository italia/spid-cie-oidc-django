from django.conf import settings
from spid_cie_oidc.onboarding.schemas.authn_requests import (
    AuthenticationRequestSpid,
    AuthenticationRequestCie
)


OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    'OIDCFED_PROVIDER_PROFILES',
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
        }
    }
)


OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILE",
    "spid"
)
