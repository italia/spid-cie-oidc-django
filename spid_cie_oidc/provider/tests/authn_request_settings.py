from copy import deepcopy

from spid_cie_oidc.entity.utils import exp_from_now, iat_now

# TODO: we need factory function to get fresh now
IAT = iat_now()
EXP = exp_from_now()

CLAIMS_SPID = {
    "userinfo": {
        "https://attributes.spid.gov.it/name": {"values": ["str", "str"]},
        "https://attributes.spid.gov.it/familyName": None,
        "https://attributes.spid.gov.it/dateOfBirth": {"value": "str"},
    },
}

CLAIMS_CIE = {
    "userinfo": {
        "given_name": {"values": ["str", "str"]},
        "family_name": None,
        "birthdate": {"value": "str"},
    },
    "id_token": {
        "given_name": {"values": ["str", "str"]},
        "family_name": None,
        "birthdate": {"value": "str"},
    },
}

AUTHN_REQUEST_SPID = {
    "client_id": "https://rp.cie.it/callback1/",
    "response_type": "code",
    "scope": ["openid", "offline_access"],
    "code_challenge": "codeChallenge",
    "code_challenge_method": "S256",
    "nonce": "12345678123456781234567812345678inpiu",
    "prompt": "consent",
    "redirect_uri": "https://rp.cie.it/callback1/",
    "acr_values": ["https://www.spid.gov.it/SpidL2", "https://www.spid.gov.it/SpidL1"],
    "claims": CLAIMS_SPID,
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd",
    "ui_locales": ["codice1", "codice2", "codice3"],
    "sub": "https://rp.cie.it/",
    "iss": "https://op.spid.agid.gov.it/",
    "aud": ["https://rp.spid.agid.gov.it/auth"],
    "iat": IAT,
    "exp": EXP,
    "jti": "a72d5df0-2415-4c7c-a44f-3988b354040b",
}

AUTHN_REQUEST_SPID_NO_CLIENT_ID = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CLIENT_ID.pop("client_id")

AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_CLAIMS["claims"]["userinfo"][
    "https://attributes.spid.gov.it/name"
]["values"] = ["str"]

AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE.pop("code_challenge")

AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CODE_CHALLENGE_METHOD.pop("code_challenge_method")

AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_CODE_CHALLENGE_METHOD["code_challenge_method"] = "S257"

AUTHN_REQUEST_SPID_NO_NONCE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_NONCE.pop("nonce")

AUTHN_REQUEST_SPID_NO_CORRECT_NONCE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_NONCE["nonce"] = "toosmall"

AUTHN_REQUEST_SPID_NO_PROMPT = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_PROMPT.pop("prompt")

AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_PROMPT["prompt"] = "no_correct"

AUTHN_REQUEST_SPID_NO_REDIRECT_URL = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_REDIRECT_URL.pop("redirect_uri")

AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_REDIRECT_URL["redirect_uri"] = "https://rp"

AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_RESPONSE_TYPE.pop("response_type")

AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_RESPONSE_TYPE["response_type"] = "codecode"

AUTHN_REQUEST_SPID_NO_SCOPE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_SCOPE.pop("scope")

AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_SCOPE["scope"] = ["offline_access"]

AUTHN_REQUEST_SPID_NO_ACR_VALUES = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_ACR_VALUES.pop("acr_values")

AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_ACR_VALUES["acr_values"] = [
    "https://www.spid.gov.it/SpidL4",
    "https://www.spid.gov.it/SpidL1",
]

AUTHN_REQUEST_SPID_NO_STATE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_STATE.pop("state")

AUTHN_REQUEST_SPID_NO_CORRECT_STATE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_STATE["state"] = "toosmall"

AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_SPID_NO_CORRECT_UI_LOCALES["ui_locales"] = "nocorrect"


AUTHN_REQUEST_CIE = deepcopy(AUTHN_REQUEST_SPID)
AUTHN_REQUEST_CIE["scope"] = ["openid", "offline_access", "email", "profile"]
AUTHN_REQUEST_CIE["prompt"] = "consent login"
AUTHN_REQUEST_CIE["claims"] = CLAIMS_CIE

AUTHN_REQUEST_CIE_NO_ACR_VALUES = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_ACR_VALUES.pop("acr_values")

AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_CORRECT_ACR_VALUES["acr_values"] = "CIE_L3"

AUTHN_REQUEST_CIE_NO_PROMPT = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_PROMPT.pop("prompt")

AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_CORRECT_PROMPT["prompt"] = "verify"

AUTHN_REQUEST_CIE_NO_SCOPE = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_SCOPE.pop("scope")

AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE = deepcopy(AUTHN_REQUEST_CIE)
AUTHN_REQUEST_CIE_NO_CORRECT_SCOPE["scope"] = "openid"
