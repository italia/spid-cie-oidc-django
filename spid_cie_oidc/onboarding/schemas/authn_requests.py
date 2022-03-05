from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, conlist, constr, validator

# TODO: Schema of claims is not genrated


class AcrValuesSpid(str, Enum):
    l1 = "https://www.spid.gov.it/SpidL1"
    l2 = "https://www.spid.gov.it/SpidL2"
    l3 = "https://www.spid.gov.it/SpidL3"


class AcrValuesCie(str, Enum):
    l1 = "CIE_L1"
    l2 = "CIE_L2"
    l3 = "CIE_L3"


class ScopeSpid(str, Enum):
    openid = "openid"
    offline_access = "offline_access"


class ScopeCie(str, Enum):
    openid = "openid"
    offline_access = "offline_access"
    profile = "profile"
    email = "email"


class ClaimsTypeEssential(BaseModel):
    essential: Optional[bool]


class ClaimsTypeStringValue(BaseModel):
    value: Optional[str]


class ClaimsTypeStringValues(BaseModel):
    values: Optional[conlist(str, max_items=2, min_items=2)]


class ClaimsType(str, Enum):
    essential = ClaimsTypeEssential
    value = ClaimsTypeStringValue
    values = ClaimsTypeStringValues


nameStr = "https://attributes.spid.gov.it/name"


class UserInfoSpid(BaseModel):
    name: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/name", default=None
    )
    family_name: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/familyName", default=None
    )
    place_of_birth: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/placeOfBirth", default=None
    )
    county_of_birth: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/countyOfBirth", default=None
    )
    date_of_birth: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/dateOfBirth", default=None
    )
    gender: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/gender", default=None
    )
    company_name: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/companyName", default=None
    )
    registered_office: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/registeredOffice", default=None
    )
    fiscal_number: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/fiscalNumber", default=None
    )
    iva_code: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/ivaCode", default=None
    )
    id_card: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/idCard", default=None
    )
    mobile_phone: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/mobilePhone", default=None
    )
    email: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/email", default=None
    )
    address: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/address", default=None
    )
    expiration_date: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/expirationDate", default=None
    )
    digital_address: Optional[dict] = Field(
        alias="https://attributes.spid.gov.it/digitalAddress", default=None
    )


class UserInfoCie(BaseModel):
    given_name: Optional[dict]
    family_name: Optional[dict]
    email: Optional[dict]
    email_verified: Optional[dict]
    gender: Optional[dict]
    birthdate: Optional[dict]
    phone_number: Optional[dict]
    phone_number_verified: Optional[dict]
    address: Optional[dict]
    place_of_birth: Optional[dict]
    document_details: Optional[dict]
    e_delivery_service: Optional[dict]
    fiscal_number: Optional[dict]
    physical_phone_number: Optional[dict]


class IdToken(UserInfoCie):
    pass


TYPES = {
    "essential": ClaimsTypeEssential,
    "value": ClaimsTypeStringValue,
    "values": ClaimsTypeStringValues,
}

CLAIMS_SPID = {"userinfo": UserInfoSpid}

CLAIMS_CIE = {"userinfo": UserInfoCie, "id_token": IdToken}


class AuthenticationRequest(BaseModel):
    client_id: HttpUrl
    response_type: Literal["code"]
    scope: List[str]
    code_challenge: str
    code_challenge_method: Literal["S256"]
    nonce: constr(min_length=32)
    redirect_uri: HttpUrl
    claims: Optional[dict]
    state: constr(min_length=32)
    # TODO: to be improved
    ui_locales: Optional[List[str]]
    sub: HttpUrl
    iss: HttpUrl
    iat: int
    exp: Optional[int]
    jti: Optional[str]
    aud: List[HttpUrl]

    @validator("claims")
    def validate_claims(cls, claims):
        for k_claim, v_claim in claims.items():
            cl = cls.get_claims()
            claims_items = cl.get(k_claim, None)
            if not claims_items:
                continue
            claims_items(**v_claim)
            for k_item, v_item in v_claim.items():
                if v_item is not None:
                    for k_type, v_type in TYPES.items():
                        v_type(**v_item)
        return claims

    @validator("scope")
    def validate_scope(cls, scope):
        if "openid" not in scope:
            raise ValueError("'scope' attribute must contain 'openid'")


class AuthenticationRequestSpid(AuthenticationRequest):
    scope: List[ScopeSpid]
    prompt: Literal["consent", "consent login", "verify"]
    acr_values: List[AcrValuesSpid]

    def get_claims() -> dict:
        return CLAIMS_SPID


class AuthenticationRequestCie(AuthenticationRequest):
    scope: List[ScopeCie]
    prompt: Literal["consent", "consent login"]
    acr_values: List[AcrValuesCie]

    def get_claims() -> dict:
        return CLAIMS_CIE
