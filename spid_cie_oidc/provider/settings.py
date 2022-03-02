from django.conf import settings
from spid_cie_oidc.onboarding.schemas.authn_requests import (
    AuthenticationRequestSpid,
    AuthenticationRequestCie
)
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataSpid, OPMetadataCie


OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    'OIDCFED_PROVIDER_PROFILES',
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
            "op_metadata": OPMetadataSpid,
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
            "op_metadata": OPMetadataCie,
        }
    }
)


OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILE",
    "spid"
)
