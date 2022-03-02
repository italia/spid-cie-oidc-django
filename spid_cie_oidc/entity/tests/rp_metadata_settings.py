from copy import deepcopy

from spid_cie_oidc.entity.tests.jwks_settings import JWKS

RP_METADATA = {
    "redirect_uris": [
        "https://rp.cie.it/callback1/",
        "https://rp.cie.it/callback2/"
    ],
    "jwks_uri": "https://registry.cie.gov.it/keys.json",
    "response_types": ["code"],
    "grant_types": ["authorization_code", "refresh_token"],
    "client_id": "https://rp.cie.it",
    "client_name": "Nome RP",
}

RP_METADATA_CIE = deepcopy(RP_METADATA)
RP_METADATA_CIE["tls_client_certificate_bound_access_tokens"] = True
RP_METADATA_CIE["application_type"] = "web"

RP_METADATA_SPID = deepcopy(RP_METADATA)

RP_METADATA_SPID_NO_REDIRECT_URIS = deepcopy(RP_METADATA_SPID)
RP_METADATA_SPID_NO_REDIRECT_URIS.pop("redirect_uris")


RP_METADATA_SPID_JWKS_AND_JWKS_URI = deepcopy(RP_METADATA_SPID)
RP_METADATA_SPID_JWKS_AND_JWKS_URI["jwks"] = JWKS
