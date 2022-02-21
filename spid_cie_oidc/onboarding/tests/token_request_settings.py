from copy import deepcopy

TOKEN_REQUEST = {
    "client_id": "https://rp.cie.it",
    "client_assertion": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiw...",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
}

TOKEN_AUTHN_CODE_REQUEST = deepcopy(TOKEN_REQUEST)
TOKEN_AUTHN_CODE_REQUEST["code"] = "usDwMnEzJPpG5oaV8x3j&"
TOKEN_AUTHN_CODE_REQUEST["code_verifier"] = "9g8S40MozM3NSqjHnhi7OnsE38jklFv2&"
TOKEN_AUTHN_CODE_REQUEST["grant_type"] = "authorization_code"

TOKEN_REFRESH_REQUEST = deepcopy(TOKEN_REQUEST)
TOKEN_REFRESH_REQUEST["grant_type"] = "refresh_token"
TOKEN_REFRESH_REQUEST["refresh_token"] = "8xLOxBtZp8"
