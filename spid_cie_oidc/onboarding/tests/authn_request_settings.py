AUTHN_REQUEST_SPID = {
    "client_id": "https://rp.cie.it/callback1/",
    "response_type": "code",
    "scope": "openid",
    "code_challenge": "codeChallenge",
    "code_challenge_method": "S256",
    "nonce": "12345678123456781234567812345678inpiu",
    "prompt": "consent login",
    "redirect_uri": "https://rp.cie.it/callback1/",
    "acr_values": "https://www.spid.gov.it/SpidL2 https://www.spid.gov.it/SpidL1",
    "claims":{
        "userinfo":{
            "given_name": {"values": ["str", "str"] },
            "family_name": None
            }
    },
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd"
}
