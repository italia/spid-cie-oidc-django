from spid_cie_oidc.entity.jwks import serialize_rsa_key, new_rsa_key

INTERMEDIARY_RSA = new_rsa_key()
INTERMEDIARY_JWK1 = serialize_rsa_key(INTERMEDIARY_RSA.priv_key, kind='private')
INTERMEDIARY_JWK1_pub = serialize_rsa_key(INTERMEDIARY_RSA.pub_key)

RP_METADATA_JWK1 = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'd': 'jEDxjcTZXBbgBV8Bgt7-qfW1FJoHDEFKFxhfMpHQQoETa-jTPhCxOD2MzYM8A-9kKc8tu9r-crTAl1PI42kPnMd283phixd5G5Tv8gSaGdnq-45ka0iRuC7TItUdDiMNb_2YzB4ZLGLNmaIKQJSGqCHEcQuRVyxJtTZwrXaMMOhDqJaWUvUQWF5C7g5O5mOVTkNKw6ujzhqcWa4N3NE-HwcbVW_9st4s1c_ng-DlwLTptaeM5j-LOeZMX1zcVlwYMi5ZkYYY6FHHjYI4nBWDtqhvf-64QaTv8exIjk8PcxHOwhfLTWiHPLk14af7U_pCzkP87WQCBgNfvt3WILQ5DQ', 'p': '75eNHkWaYQMgzVfFwif5uftSxqOhFU6VkxNKdqoRuFxJuVTO-M-vbQc3BwPxms2xrpizU6zGcoPGPvccDi0G040wZh34pWDVABMgGMKXKmeTwj8FuM1DzOVq8DKHmdrhk1gaQbPAP8JVOVYK7uh_lG5wmz3X-En1McMk-E8g8Ic', 'q': '0Sny6DLNtDP1_B9qiyCaMtRqPSAUZ1ohCZRlBT6-IGRR31Kt5S2JcVNDnF5w4dunlDY4nhIBZ0v0VyzWKgDXj6qrFY1pm1iE29gW227YsVRWQU8xWGpBwEu8nxNMr0u0zfe0QEGWU4RvNAsZPRa31HU87Vm7I3NSZ34DZsCZJoc', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}
RP_METADATA_JWK1_pub = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}

rp_onboarding_data = dict(
    name="RP Test",
    sub="http://rp-test.it/oidc/rp/",
    type="openid_relying_party",
    metadata_policy={"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True,
    jwks = [RP_METADATA_JWK1_pub]
)

rp_conf = {
    "sub": rp_onboarding_data["sub"],
    "jwks" : [RP_METADATA_JWK1],
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

RP_CONF = {
  "iss": "http://127.0.0.1:8000/oidc/rp/",
  "sub": "http://127.0.0.1:8000/oidc/rp/",
  "jwks": {
    "keys": [RP_METADATA_JWK1_pub]
  },
  "metadata": {
    "openid_relying_party": {
      "application_type": "web",
      "client_id": "http://127.0.0.1:8000/oidc/rp/",
      "client_registration_types": [
        "automatic"
      ],
      "jwks": {
        "keys": [
          {
            "kty": "RSA",
            "use": "sig",
            "n": "5s4qi1Ta-sEuKb5rJ8TzHmyGKaSu89pIXIi6w4Ekx6GL56mJDNE_MWJHsFjWXajfMdMQmZrSXAvLtXxmbhUui9Mq_IormhmEyyEJS0SyE9UKTxWzi0yd_n_C7OjFBhM-0ZyUlgl81E_sr-35P1A6b5WSYwMvRSR-P9yx_NI-XBQ48G_zdmk3CbuuzZsXZqqgj5U7OGWH-4Huosn9nH3FVkwX0OlWkgWM-J9DEWzGBjl9hfbbrMtM_obljHL2NfT6RJYER2IpdI8RCyQS3sMPt6ZHDskmuNlyMDNATCChXQJLnltwEjxcgvzjw_G9J25DwfdfVEhDF_0kCp44UMmS3Q",
            "e": "AQAB",
            "kid": "2HnoFS3YnC9tjiCaivhWLVUJ3AxwGGz_98uRFaqMEEs"
          }
        ]
      },
      "client_name": "Name of this service called https://rp.example.it/",
      "contacts": [
        "ops@rp.example.it"
      ],
      "grant_types": [
        "refresh_token",
        "authorization_code"
      ],
      "redirect_uris": [
        "http://127.0.0.1:8000/oidc/rp/callback"
      ],
      "response_types": [
        "code"
      ],
      "subject_type": "pairwise"
    }
  },
  "trust_marks": [
    {
      "id": "https://www.spid.gov.it/openid-federation/agreement/sp-public/",
      "trust_mark": "eyJhbGciOiJSUzI1NiIsImtpZCI6IkZpZll4MDNibm9zRDhtNmdZUUlmTkhOUDljTV9TYW05VGM1bkxsb0lJcmMifQ.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvIiwic3ViIjoiaHR0cDovLzEyNy4wLjAuMTo4MDAwL29pZGMvcnAvIiwiaWF0IjoxNjQ1NjEyNDAxLCJpZCI6Imh0dHBzOi8vd3d3LnNwaWQuZ292Lml0L2NlcnRpZmljYXRpb24vcnAiLCJtYXJrIjoiaHR0cHM6Ly93d3cuYWdpZC5nb3YuaXQvdGhlbWVzL2N1c3RvbS9hZ2lkL2xvZ28uc3ZnIiwicmVmIjoiaHR0cHM6Ly9kb2NzLml0YWxpYS5pdC9pdGFsaWEvc3BpZC9zcGlkLXJlZ29sZS10ZWNuaWNoZS1vaWRjL2l0L3N0YWJpbGUvaW5kZXguaHRtbCJ9.mSPNR0AOPBn3UNJAIbrWUMQ8vGTetQajpa3i59JDKDXYWqo2TUGh4AQBghCiG3qqV9cl-hleLtuwoeZ1InKHeslTLftVdcR3meeMLs3mLobHYr26Mi7pC7-jx1ZFVyk4GXl7mn9WVSQGEUOiuhL01tdlUfxf0TJSFSOMEZGpCA3hXroLOnEl3FjkAw7sPvjfImsbadbHVusb72HTTs1n5Xo7z3As3fDWHcxD-fvvq0beu9cx-L2sT4YaNC-ELd1M3m5r0NIjjEUAt4Gnot-l5Z3-C_bA41uvh2hX34U_fGZ6jpmuluJo1Lqi26N8LTB-Rbu0UMaZnkRg9E72_YRZig"
    }
  ],
  "authority_hints": [
    "http://127.0.0.1:8000/"
  ]
}

intermediary_conf = {
    "sub": "http://intermediary-test",
    "metadata": {
        "federation_entity": {
            "contacts": ["ops@localhost"],
            "federation_api_endpoint": "http://intermediary-test/fetch",
            "homepage_uri": "http://intermediary-test",
            "name": "example Intermediate",
        }
    },
    "trust_marks": [],
    "authority_hints": ["http://testserver/"],
    "is_active": True,
    "jwks": [INTERMEDIARY_JWK1]
}
intermediary_onboarding_data = dict(
    name="intermediary-test",
    sub="http://intermediary-test",
    type="federation_entity",
    # metadata_policy = {"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True,
    jwks = [INTERMEDIARY_JWK1_pub]
)


TRUST_MARK_PAYLOAD = {
    "iss": "$.issuer_sub",
    "sub": "$.sub",
    "iat": 1579621160,
    "id": "https://www.spid.gov.it/certification/rp",
    "mark": "https://www.agid.gov.it/themes/custom/agid/logo.svg",
    "ref": "https://docs.italia.it/italia/spid/spid-regole-tecniche-oidc/it/stabile/index.html",
}

RP_PROFILE = {
    "name": "SPID Public SP",
    "profile_category": "openid_relying_party",
    "profile_id": "https://www.spid.gov.it/certification/rp",
    "trust_mark_template": TRUST_MARK_PAYLOAD,
}

RP_METADATA = {
    "openid_relying_party": {
        "application_type": "web",
        "client_registration_types": ["automatic"],
        "client_name": f"Name of this service called {rp_onboarding_data['sub']}",
        "contacts": ["ops@rp.example.it"],
        "grant_types": ["refresh_token", "authorization_code"],
        "jwks": {"keys": [RP_METADATA_JWK1_pub]},
        "redirect_uris": [f"{rp_onboarding_data['sub']}/callback/"],
        "response_types": ["code"],
        "subject_type": "pairwise",
    }
}
