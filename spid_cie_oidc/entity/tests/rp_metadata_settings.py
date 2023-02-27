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
    "organization_name": "Tal dei tali"
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


RP_METADATA_JWK1 = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'd': 'jEDxjcTZXBbgBV8Bgt7-qfW1FJoHDEFKFxhfMpHQQoETa-jTPhCxOD2MzYM8A-9kKc8tu9r-crTAl1PI42kPnMd283phixd5G5Tv8gSaGdnq-45ka0iRuC7TItUdDiMNb_2YzB4ZLGLNmaIKQJSGqCHEcQuRVyxJtTZwrXaMMOhDqJaWUvUQWF5C7g5O5mOVTkNKw6ujzhqcWa4N3NE-HwcbVW_9st4s1c_ng-DlwLTptaeM5j-LOeZMX1zcVlwYMi5ZkYYY6FHHjYI4nBWDtqhvf-64QaTv8exIjk8PcxHOwhfLTWiHPLk14af7U_pCzkP87WQCBgNfvt3WILQ5DQ', 'p': '75eNHkWaYQMgzVfFwif5uftSxqOhFU6VkxNKdqoRuFxJuVTO-M-vbQc3BwPxms2xrpizU6zGcoPGPvccDi0G040wZh34pWDVABMgGMKXKmeTwj8FuM1DzOVq8DKHmdrhk1gaQbPAP8JVOVYK7uh_lG5wmz3X-En1McMk-E8g8Ic', 'q': '0Sny6DLNtDP1_B9qiyCaMtRqPSAUZ1ohCZRlBT6-IGRR31Kt5S2JcVNDnF5w4dunlDY4nhIBZ0v0VyzWKgDXj6qrFY1pm1iE29gW227YsVRWQU8xWGpBwEu8nxNMr0u0zfe0QEGWU4RvNAsZPRa31HU87Vm7I3NSZ34DZsCZJoc', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}
RP_METADATA_JWK1_pub = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}

rp_onboarding_data = dict(
    name="RP Test",
    sub="http://rp-test.it/oidc/rp/",
    type="openid_relying_party",
    metadata_policy={"openid_relying_party": {"scope": {"value": ["openid"]}}},
    is_active=True,
    jwks = [RP_METADATA_JWK1_pub]
)

rp_conf = {
    "sub": rp_onboarding_data["sub"],
    "jwks_fed" : [RP_METADATA_JWK1],
    "jwks_core" : [RP_METADATA_JWK1],
    "metadata": {
        "openid_relying_party": {
            "application_type": "web",
            "client_registration_types": ["automatic"],
            "client_name": "Name of this service called http://rp-test.it/oidc/rp/",
            "contacts": ["ops@rp.example.it"],
            "grant_types": ["refresh_token", "authorization_code"],
            "redirect_uris": ["http://rp-test.it/oidc/rp/callback/"],
            "response_types": ["code"],
            "subject_type": "pairwise",
            "client_id": "http://rp-test.it/oidc/rp/",
            "jwks": {"keys": [RP_METADATA_JWK1_pub]},
        }
    },
    "authority_hints": ["http://testserver/"],
    "is_active": True,
}

RP_CONF_AS_JSON = {
  "iss": rp_conf["sub"],
  "sub": rp_conf["sub"],
  "jwks": {
    "keys": [RP_METADATA_JWK1_pub]
  },
  "metadata": rp_conf["metadata"],
  "authority_hints":rp_conf["authority_hints"]
}
