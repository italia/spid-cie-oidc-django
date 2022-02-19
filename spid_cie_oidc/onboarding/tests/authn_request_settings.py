from copy import deepcopy

AUTHN_REQUEST_SPID = {
    "client_id": "https://rp.cie.it/callback1/",
    "response_type": "code",
    "scope": ["openid", "offline_access"],
    "code_challenge": "codeChallenge",
    "code_challenge_method": "S256",
    "nonce": "12345678123456781234567812345678inpiu",
    "prompt": "verify",
    "redirect_uri": "https://rp.cie.it/callback1/",
    "acr_values": ["https://www.spid.gov.it/SpidL2", "https://www.spid.gov.it/SpidL1"],
    "claims":{
        "userinfo":{
            "given_name": {"values": ["str", "str"] },
            "family_name": None,
            "birthdate": {"value": "str" }
            },
        "id_token":{
            "given_name": {"values": ["str", "str"] },
            "family_name": None,
            "birthdate": {"value": "str" }
            }
    },
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd",
    "ui_locales": ["codice1", "codice2", "codice3"]
}

AUTHN_REQUEST_CIE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_CIE["scope"] = ["openid", "offline_access", "email", "profile"]
AUTHN_REQUEST_CIE["prompt"] = "consent login"
AUTHN_REQUEST_CIE["acr_values"] = ["CIE_L2", "CIE_L1"]

AUTHN_REQUEST_SPID_NO_CLIENT_ID = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CLIENT_ID.pop("client_id")

AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS["claims"].pop("id_token")
AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS["claims"]["userinfo"]["given_name"]["values"] = ["str"]
