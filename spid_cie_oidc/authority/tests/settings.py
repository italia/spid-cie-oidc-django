from spid_cie_oidc.entity.jwks import create_jwk
from spid_cie_oidc.entity.jwks import new_rsa_key, serialize_rsa_key

rp_onboarding_data = dict(
    name="RP Test",
    sub="http://rp-test/oidc/rp",
    type="openid_relying_party",
    metadata_policy={"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True,
)

RP_METADATA_JWK1 = serialize_rsa_key(new_rsa_key().priv_key, 'private')
RP_METADATA_JWK1_pub = serialize_rsa_key(new_rsa_key().pub_key)

rp_conf = {
    "sub": rp_onboarding_data["sub"],
    "metadata": {
        "openid_relying_party": {
            "application_type": "web",
            "client_registration_types": ["automatic"],
            "client_name": "Name of this service called https://rp.example.it/spid",
            "contacts": ["ops@rp.example.it"],
            "grant_types": ["refresh_token", "authorization_code"],
            "redirect_uris": ["https://rp.example.it/spid/callback"],
            "response_types": ["code"],
            "subject_type": "pairwise",
            "jwks" : {
                "keys": [RP_METADATA_JWK1]
            }
        }
    },
    "authority_hints": ["http://testserver/"],
    "is_active": True
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
    "is_active": True,
}
intermediary_onboarding_data = dict(
    name="intermediary-test",
    sub="http://intermediary-test",
    type="federation_entity",
    # metadata_policy = {"openid_relying_party": {"scopes": {"value": ["openid"]}}},
    is_active=True,
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
        "jwks" : {
            "keys": [RP_METADATA_JWK1]
        },
        "redirect_uris": [f"{rp_onboarding_data['sub']}/spid/callback"],
        "response_types": ["code"],
        "subject_type": "pairwise",
    }
}
