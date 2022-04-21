from copy import deepcopy

from spid_cie_oidc.entity.tests.jwks_settings import JWKS

RP_METADATA = {
    "redirect_uris": [
        "https://rp.example.it/spid/callback1/",
        "https://rp.example.it/spid/callback2/",
    ],
    "jwks_uri": "https://registry.cie.gov.it/keys.json",
    "response_types": ["code"],
    "grant_types": ["authorization_code", "refresh_token"],
    "client_id": "https://rp.example.it/spid",
    "client_name": "Nome RP",
    "contacts": ["ops@rp.example.it"],
    "subject_type": "pairwise", 
    "logo_uri": [
          "https://rp.example.it/logo_small.jpg",
          "https://rp.example.it/logo_big.jpg"
    ],
    "scope" : ["openid", "offline_access", "profile"],
}

RP_METADATA_CIE = deepcopy(RP_METADATA)
RP_METADATA_CIE["tls_client_certificate_bound_access_tokens"] = True
RP_METADATA_CIE["application_type"] = "web"

RP_METADATA_SPID = deepcopy(RP_METADATA)

RP_METADATA_SPID_NO_REDIRECT_URIS = deepcopy(RP_METADATA_SPID)
RP_METADATA_SPID_NO_REDIRECT_URIS.pop("redirect_uris")


RP_METADATA_SPID_JWKS_AND_JWKS_URI = deepcopy(RP_METADATA_SPID)
RP_METADATA_SPID_JWKS_AND_JWKS_URI["jwks"] = JWKS

RP_METADATA_CIE_JWKS_AND_JWKS_URI = deepcopy(RP_METADATA_CIE)
RP_METADATA_CIE_JWKS_AND_JWKS_URI["jwks"] = JWKS

RP_METADATA_CIE_NO_REDIRECT_URIS = deepcopy(RP_METADATA_CIE)
RP_METADATA_CIE_NO_REDIRECT_URIS.pop("redirect_uris")

RP_METADATA_SPID_NOJWKS_NOJWKS_URI = deepcopy(RP_METADATA_SPID)
RP_METADATA_SPID_NOJWKS_NOJWKS_URI.pop("jwks_uri")

RP_METADATA_CIE_NOJWKS_NOJWKS_URI = deepcopy(RP_METADATA_CIE)
RP_METADATA_CIE_NOJWKS_NOJWKS_URI.pop("jwks_uri")
