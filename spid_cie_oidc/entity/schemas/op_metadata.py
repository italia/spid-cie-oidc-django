from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, root_validator

from .jwks import JwksCie


class ScopeSupported(str, Enum):
    openid = "openid"
    offline_access = "offline_access"
    profile = "profile"
    email = "email"


class ResponseModesSupported(str, Enum):
    form_post = ("form_post",)
    query = "query"


class GrantTypeSupported(str, Enum):
    refresh_token = "refresh_token"  # nosec - B105
    authorization_code = "authorization_code"


class AcrValuesSupported(str, Enum):
    spid_l1 = "https://www.spid.gov.it/SpidL1"
    spid_l2 = "https://www.spid.gov.it/SpidL2"
    spid_l3 = "https://www.spid.gov.it/SpidL3"


class SigningAlgValuesSupported(str, Enum):
    es256 = "ES256"
    es384 = "ES384"
    es512 = "ES512"
    rs256 = "RS256"
    rs384 = "RS384"
    rs512 = "RS512"
    # TODO: to be confirmed
    # ps256 = "PS256"
    # ps384 = "PS384"
    # ps512 = "PS512"


class EncryptionAlgValuesSupported(str, Enum):
    rsa_oaep = "RSA-OAEP"
    ras_oaep_256 = "RSA-OAEP-256"


class EncryptionEncValuesSupported(str, Enum):
    a128cbc_hs256 = "A128CBC-HS256"
    a192cbc_hs384 = "A192CBC-HS384"
    a256cbc_hs512 = "A256CBC-HS512"
    a128gcm = "A128GCM"
    a192gcm = "A192GCM"
    a256gcm = "A256GCM"
    rsa_oaep_256 = "RSA-OAEP-256"


class ClaimsSupported(str, Enum):
    given_name = "given_name"
    family_name = "family_name"
    email = "email"
    email_verified = "email_verified"
    gender = "gender"
    birthdate = "birthdate"
    phone_number = "phone_number"
    phone_number_verified = "phone_number_verified"
    place_of_birth = "place_of_birth"
    address = "address"
    document_details = "document_details"
    https_attributes_eid_gov_it_e_delivery_service = (
        "https://attributes.eid.gov.it/e_delivery_service"
    )
    https_attributes_eid_gov_it_fiscal_number = (
        "https://attributes.eid.gov.it/fiscal_number"
    )
    https_attributes_eid_gov_it_idANPR = "https://attributes.eid.gov.it/idANPR"
    https_attributes_eid_gov_it_physical_phone_number = (
        "https://attributes.eid.gov.it/physical_phone_number"
    )


class OPMetadata(BaseModel):
    organization_name: str
    issuer: HttpUrl
    authorization_endpoint: HttpUrl
    token_endpoint: HttpUrl
    userinfo_endpoint: HttpUrl
    introspection_endpoint: HttpUrl
    revocation_endpoint: HttpUrl
    token_endpoint_auth_signing_alg_values_supported: List[SigningAlgValuesSupported]
    id_token_encryption_alg_values_supported: List[EncryptionAlgValuesSupported]
    id_token_encryption_enc_values_supported: List[EncryptionEncValuesSupported]
    userinfo_encryption_alg_values_supported: List[EncryptionAlgValuesSupported]
    userinfo_encryption_enc_values_supported: List[EncryptionEncValuesSupported]
    request_object_encryption_alg_values_supported: List[EncryptionAlgValuesSupported]
    request_object_encryption_enc_values_supported: List[EncryptionEncValuesSupported]
    id_token_signing_alg_values_supported: List[SigningAlgValuesSupported]
    userinfo_signing_alg_values_supported: List[SigningAlgValuesSupported]
    request_object_signing_alg_values_supported: List[SigningAlgValuesSupported]
    token_endpoint_auth_methods_supported = ["private_key_jwt"]
    subject_types_supported = ["pairwise"]
    request_parameter_supported = True
    acr_values_supported: List[AcrValuesSupported]
    signed_jwks_uri: Optional[HttpUrl]
    jwks_uri: Optional[HttpUrl]
    jwks: Optional[JwksCie]

    @root_validator(pre=False)
    def validate(cls, values):
        jwks_there = False
        for i in ("jwks_uri", "jwks", "signed_jwks_uri"):
            if values.get(i):
                jwks_there = True
                break
        
        if not jwks_there:
            raise ValueError(
                "one of signed_jwks_uri or jwks_uri or jwks must be set"
            )
        return values


class OPMetadataCie(OPMetadata):
    scopes_supported: List[ScopeSupported]
    response_types_supported = ["code"]
    response_modes_supported: List[ResponseModesSupported]
    grant_types_supported: List[GrantTypeSupported]
    claims_supported: List[ClaimsSupported]
    claims_parameter_supported = True
    tls_client_certificate_bound_access_tokens = True
    authorization_response_iss_parameter_supported = True


class OPMetadataSpid(OPMetadata):
    op_name: Optional[str]
    op_uri: Optional[str]
