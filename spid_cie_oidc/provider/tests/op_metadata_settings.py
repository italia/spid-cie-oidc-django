from copy import deepcopy

OP_METADATA = {
    "issuer": "https://idserver.servizicie.interno.gov.it/op/",
    "authorization_endpoint": "https://idserver.servizicie.interno.gov.it/op/auth",
    "token_endpoint": "https://idserver.servizicie.interno.gov.it/op/token",
    "userinfo_endpoint": "https://idserver.servizicie.interno.gov.it/op/userinfo",
    "introspection_endpoint": "https://idserver.servizicie.interno.gov.it/op/introspect",
    "revocation_endpoint": "https://idserver.servizicie.interno.gov.it/op/revoke",
    "jwks_uri": "https://registry.cie.gov.it/.well-known/jwks.json",
    "subject_types_supported":["pairwise"],
    "id_token_encryption_alg_values_supported": ["RSA-OAEP"],
    "userinfo_signing_alg_values_supported": ["ES256"],
    "request_object_encryption_enc_values_supported": ["A256CBC-HS512"],
    "token_endpoint_auth_methods_supported": ["private_key_jwt"],
    "userinfo_encryption_alg_values_supported": ["RSA-OAEP"],
    "id_token_encryption_enc_values_supported": ["A256CBC-HS512"],
    "id_token_signing_alg_values_supported": ["ES256"],
    "request_object_encryption_alg_values_supported": ["RSA-OAEP"],
    "request_object_signing_alg_values_supported": ["ES256"],
    "userinfo_encryption_enc_values_supported": ["A256CBC-HS512"],
   "request_parameter_supported": True,
    "subject_types_supported":["pairwise"],
    "token_endpoint_auth_methods_supported":["private_key_jwt"],
}

OP_METADATA_CIE = deepcopy(OP_METADATA)
OP_METADATA_CIE["scopes_supported"] = ["openid","offline_access","email"]
OP_METADATA_CIE["response_types_supported"] =  ["code"]
OP_METADATA_CIE["response_modes_supported"] =  ["query","form_post"]
OP_METADATA_CIE["grant_types_supported"] =  ["authorization_code","refresh_token"]
OP_METADATA_CIE["acr_values_supported"] =  ["CIE_L1", "CIE_L3"]
OP_METADATA_CIE["claims_supported"] = [
        "given_name",
        "family_name",
        "email",
        "email_verified",
        "gender",
        "birthdate",
        "phone_number",
        "phone_number_verified",
        "place_of_birth",
        "address",
        "document_details",
        "https://attributes.eid.gov.it/e_delivery_service",
        "https://attributes.eid.gov.it/fiscal_number",
        "https://attributes.eid.gov.it/idANPR",
        "https://attributes.eid.gov.it/physical_phone_number"
    ]
OP_METADATA_CIE["claims_parameter_supported"] =  True
OP_METADATA_CIE["tls_client_certificate_bound_access_tokens"] =  True
OP_METADATA_CIE["authorization_response_iss_parameter_supported"] =  True


OP_METADATA_CIE_JWKS_AND_JWKS_URI = deepcopy(OP_METADATA_CIE)
OP_METADATA_CIE_JWKS_AND_JWKS_URI["jwks"] = {
        "keys": [
            { 
                "kty": "EC",
                "kid": "NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs",
                "use": "sig",
                "crv": "P-256",
                "x": "2jM2df3IjB9VYQ0yz373-6EEot_1TBuTRaRYafMi5K0",
                "y": "h6Zlz6XReK0L-iu4ZgxlozJEXgTGUFuuDl7o8b_8JnM",
            },
            { 
                "kty": "EC",
                "kid": "EF71iSaosbC5C4tC6Syq1Gm647M",
                "use": "enc",
                "crv": "P-256",
                "x": "QI31cvWP4GwnWIi-Z0IYHauQ4nPCk8Vf1BHoPazGqEc",
                "y": "DBwf8t9-abpXGtTDlZ8njjxAb33kOMrOqiGsd9oRxr0"
            }
        ]
    }