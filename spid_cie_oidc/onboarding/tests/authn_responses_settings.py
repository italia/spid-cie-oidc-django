from copy import deepcopy

AUTHN_RESPONSE_SPID = {
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&",
}

AUTHN_RESPONSE_CIE = deepcopy(AUTHN_RESPONSE_SPID)
AUTHN_RESPONSE_CIE["iss"] = "https://idserver.servizicie.interno.gov.it"

AUTHN_ERROR_RESPONSE = {
    "error_description": "request%20malformata&",
    "code":"usDwMnEzJPpG5oaV8x3j&",
    "state": "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd&"
}

AUTHN_ERROR_RESPONSE_SPID = deepcopy(AUTHN_ERROR_RESPONSE)
AUTHN_ERROR_RESPONSE_SPID["error"] = "invalid_request"

AUTHN_ERROR_RESPONSE_CIE = deepcopy(AUTHN_ERROR_RESPONSE)
AUTHN_ERROR_RESPONSE_CIE["error"] = "unsupported_response_type"
AUTHN_ERROR_RESPONSE_CIE["iss"] = "https://idserver.servizicie.interno.gov.it"