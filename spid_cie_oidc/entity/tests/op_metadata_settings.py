from copy import deepcopy

from spid_cie_oidc.entity.tests.jwks_settings import JWKS, JWKS_WITH_N_AND_EC_NO_CORRECT

OP_METADATA = {
    "issuer": "https://idserver.servizicie.interno.gov.it/op/",
    "authorization_endpoint": "https://idserver.servizicie.interno.gov.it/op/auth",
    "token_endpoint": "https://idserver.servizicie.interno.gov.it/op/token",
    "userinfo_endpoint": "https://idserver.servizicie.interno.gov.it/op/userinfo",
    "introspection_endpoint": "https://idserver.servizicie.interno.gov.it/op/introspect",
    "revocation_endpoint": "https://idserver.servizicie.interno.gov.it/op/revoke",
    "jwks_uri": "https://idserver.servizicie.interno.gov.it/.well-known/jwks.json",
    "subject_types_supported": ["pairwise"],
    "token_endpoint_auth_signing_alg_values_supported" : ["ES256"],
    "id_token_encryption_alg_values_supported": ["RSA-OAEP"],
    "request_object_encryption_enc_values_supported": ["A256CBC-HS512"],
    "token_endpoint_auth_methods_supported": ["private_key_jwt"],
    "userinfo_encryption_alg_values_supported": ["RSA-OAEP"],
    "id_token_encryption_enc_values_supported": ["A256CBC-HS512"],
    "id_token_signing_alg_values_supported": ["ES256"],
    "userinfo_signing_alg_values_supported": ["ES256"],
    "request_object_encryption_alg_values_supported": ["RSA-OAEP"],
    "request_object_signing_alg_values_supported": ["ES256"],
    "userinfo_encryption_enc_values_supported": ["A256CBC-HS512"],
    "request_parameter_supported": True,
    "subject_types_supported": ["pairwise"],
    "token_endpoint_auth_methods_supported": ["private_key_jwt"],
    "op_name": "Agenzia per l’Italia Digitale",
    "op_uri": "https://www.agid.gov.it",
    "acr_values_supported":[
        "https://www.spid.gov.it/SpidL1",
        "https://www.spid.gov.it/SpidL2",
        "https://www.spid.gov.it/SpidL3"
    ],
    "organization_name": "Tal dei tali"
}

OP_METADATA_CIE = deepcopy(OP_METADATA)
OP_METADATA_CIE["scopes_supported"] = ["openid", "offline_access", "email"]
OP_METADATA_CIE["response_types_supported"] = ["code"]
OP_METADATA_CIE["response_modes_supported"] = ["query", "form_post"]
OP_METADATA_CIE["grant_types_supported"] = ["authorization_code", "refresh_token"]
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
    "https://attributes.eid.gov.it/physical_phone_number",
]
OP_METADATA_CIE["claims_parameter_supported"] = True
OP_METADATA_CIE["tls_client_certificate_bound_access_tokens"] = True
OP_METADATA_CIE["authorization_response_iss_parameter_supported"] = True
OP_METADATA_CIE["userinfo_signing_alg_values_supported"] = ["ES256"]


OP_METADATA_CIE_JWKS_AND_JWKS_URI = deepcopy(OP_METADATA_CIE)
OP_METADATA_CIE_JWKS_AND_JWKS_URI["jwks"] = JWKS

OP_METADATA_CIE_JWKS_URI_NO_CORRECT = deepcopy(OP_METADATA_CIE)
OP_METADATA_CIE_JWKS_URI_NO_CORRECT[
    "jwks_uri"
] = "https://registry.cie.gov.it/.well-known/"

OP_METADATA_SPID = deepcopy(OP_METADATA)
OP_METADATA_SPID["op_name"] = "Agenzia per l’Italia Digitale"
OP_METADATA_SPID["op_uri"] = "https://www.agid.gov.it"
OP_METADATA_SPID["userinfo_signing_alg_values_supported"] = ["RS384"]
OP_METADATA_SPID["acr_values_supported"] = [
    "https://www.spid.gov.it/SpidL1",
    "https://www.spid.gov.it/SpidL2",
    "https://www.spid.gov.it/SpidL3",
]

OP_METADATA_SPID_JWKS_AND_JWKS_URI = deepcopy(OP_METADATA_SPID)
OP_METADATA_SPID_JWKS_AND_JWKS_URI["jwks"] = JWKS

OP_METADATA_SPID_JWKS_NO_JWKS_URI = deepcopy(OP_METADATA_SPID_JWKS_AND_JWKS_URI)
OP_METADATA_SPID_JWKS_NO_JWKS_URI.pop("jwks_uri")

OP_METADATA_SPID_JWKS_EC_NO_CORRECT = deepcopy(OP_METADATA_SPID_JWKS_NO_JWKS_URI)
OP_METADATA_SPID_JWKS_EC_NO_CORRECT["jwks"] = JWKS_WITH_N_AND_EC_NO_CORRECT
