from spid_cie_oidc.entity.jwks import create_jwk

rp_onboarding_data = dict(
    name = "RP Test",
    sub = "http://rp-test/oidc/rp",
    type = "openid_relying_party",
    
    metadata_policy = {"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True
)

rp_conf = {
    "sub": rp_onboarding_data['sub'],
    "metadata": {
        "openid_relying_party": {
            "application_type": "web",
            "client_registration_types": ["automatic"],
            "client_name": "Name of this service called https://rp.example.it/spid",
            "contacts": ["ops@rp.example.it"],
            "grant_types": ["refresh_token", "authorization_code"],
            "redirect_uris": ["https://rp.example.it/spid/callback"],
            "response_types": ["code"],
            "subject_type": "pairwise"
        }
    },
    "authority_hints": ["http://testserver/"],
    "is_active" : True
}

intermediary_conf = {
    "sub": "http://intermediary-test",
    "metadata": {
        "federation_entity": {
            "contacts": ["ops@localhost"],
            "federation_api_endpoint": "http://intermediary-test/fetch",
            "homepage_uri": f"http://intermediary-test",
            "name": "example Intermediate",
        }
    },
    "trust_marks": [create_jwk()],
    "authority_hints": ["http://testserver/"],
    "is_active" : True
}
intermediary_onboarding_data = dict(
    name = "intermediary-test",
    sub = "http://intermediary-test",
    type = "federation_entity",
    
    # metadata_policy = {"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True
)


TRUST_MARK_PAYLOAD = {
    "iss": "$.issuer_sub",
    "sub": "$.sub",
    "iat": 1579621160,
    "id": "https://www.spid.gov.it/certification/rp",
    "mark": "https://www.agid.gov.it/themes/custom/agid/logo.svg",
    "ref": "https://docs.italia.it/italia/spid/spid-regole-tecniche-oidc/it/stabile/index.html"
}

RP_PROFILE = {
    "name": "SPID Public SP",
    "profile_category": "openid_relying_party",
    "profile_id": "https://www.spid.gov.it/openid-federation/agreement/sp-public/",
    "trust_mark_template": TRUST_MARK_PAYLOAD
}

RP_METADATA = {
    "openid_relying_party": {
        "application_type": "web",
        "client_registration_types": ["automatic"],
        "client_name": f"Name of this service called {rp_onboarding_data['sub']}",
        "contacts": ["ops@rp.example.it"],
        "grant_types": ["refresh_token", "authorization_code"],
        "jwks": {
            "kty": "RSA",
            "n": "1cE1PyQiBkmwO4TT30HGUwegdPZ9iKvuwQezUYOe8LqGol_6sUgxAf67_KbAeP1PMrmGH6d-AgNIT2Taa0OAtqyRUTLhG8rl7gT3_Jzwt2mOJu2JI4MfWcQxa-ZtzM8PPr7JUzWUzhHO7Nb1MfBm_fqB20cRcHOS_fvu3PqY-C-t33z3JYeDD_PsvSs2-WLlUiMDf9ILp0rVatF4GTPwvEp7VLCqCf1lLSLIxuuTVI0sc1j3xPbyv4MO_33fTmoAOVDmkUnhi2igLgw_tjc2-iu_4-r2qsKbotGiTu6y1RQrHc8xcrQmfqJ8FUwqAcpgQnlsekEHc6lWx9262Anobw",
            "e": "AQAB",
            "kid": "2C3zbeQjgx3jk-CHSqK3pLhdPeV9Fn5eSBPMNUp7vQk",
        },
        "redirect_uris": [f"{rp_onboarding_data['sub']}/spid/callback"],
        "response_types": ["code"],
        "subject_type": "pairwise",
    }
}
