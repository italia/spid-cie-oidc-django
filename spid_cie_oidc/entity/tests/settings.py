from spid_cie_oidc.entity.jwks import create_jwk

TA_SUB = "http://testserver/"
FA_METADATA = {
    "federation_entity": {
        "contacts": ["ops@localhost"],
        "federation_api_endpoint": f"{TA_SUB}/fetch",
        "homepage_uri": f"{TA_SUB}",
        "name": "example TA",
    }
}
TM_ISSUERS = {
    "https://www.spid.gov.it/certification/rp/public": [
        TA_SUB,
        "https://public.intermediary.spid.it",
    ],
    "https://www.spid.gov.it/certification/rp/private": [
        TA_SUB,
        "https://private.other.intermediary.it",
    ],
    "https://sgd.aa.it/onboarding": ["https://sgd.aa.it"],
}
FA_CONSTRAINTS = {"max_path_length": 1}

ta_conf_data = dict(
    sub=TA_SUB,
    metadata=FA_METADATA,
    constraints=FA_CONSTRAINTS,
    is_active=1,
    trust_marks_issuers=TM_ISSUERS
)
