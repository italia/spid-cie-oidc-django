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

AUTHN_REQUEST_CIE = {
    "client_id": "https://rp.cie.it/callback1/",
    "response_type": "code",
    "scope": ["openid", "offline_access", "email", "profile"],
    "code_challenge": "codeChallenge",
    "code_challenge_method": "S256",
    "nonce": "12345678123456781234567812345678inpiu",
    "prompt": "consent login",
    "redirect_uri": "https://rp.cie.it/callback1/",
    "acr_values": ["CIE_L2", "CIE_L1"],
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

AUTHN_RESPONSE_SPID = {
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&",
}

AUTHN_RESPONSE_CIE = {
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&",
    "iss": "https://idserver.servizicie.interno.gov.it"
}

AUTHN_ERROR_RESPONSE_SPID = {
    "error": "invalid_request",
    "error_description": "request%20malformata&",
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&"
}

AUTHN_ERROR_RESPONSE_CIE = {
    "error": "unsupported_response_type",
    "error_description": "hai sbagliato",
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&",
    "iss": "https://idserver.servizicie.interno.gov.it"
}

TOKEN_AUTHN_CODE_REQUEST = {
    "client_id": "https://rp.cie.it",
    "client_assertion": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiw...",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "code_verifier": "9g8S40MozM3NSqjHnhi7OnsE38jklFv2&",
    "grant_type": "authorization_code"
}

TOKEN_REFRESH_REQUEST = {
    "client_id": "https://rp.cie.it",
    "client_assertion": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiw...",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "grant_type": "refresh_token",
    "refresh_token": "8xLOxBtZp8"
}
