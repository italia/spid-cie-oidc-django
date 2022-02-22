import datetime
from typing import List, Literal

from django.utils import timezone
from pydantic import BaseModel, HttpUrl, constr, validator


class TokenRequest(BaseModel):
    client_id: HttpUrl
    client_assertion: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722
    client_assertion_type: Literal[
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]


class TokenAuthnCodeRequest(TokenRequest):
    # TODO: is 1*VSCHAR
    code: str
    # TODO: is 43*128unreserved, where unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
    code_verifier: str
    grant_type: Literal["authorization_code"]


class TokenRefreshRequest(TokenRequest):
    grant_type: Literal["refresh_token"]
    refresh_token: str

MIN_IAT_MIN = 5

class JwtClientAssertionStructure(BaseModel):
    iss: HttpUrl
    sub: HttpUrl
    iat: int
    exp: int
    jti: str

    @validator("exp")
    def validate_exp(cls, exp):
        now = int(timezone.localtime().timestamp())
        if exp <= now:
            raise ValueError('exp MUST be in the future')

    @validator("iat")
    def validate_iat(cls, iat):
        now = int(datetime.datetime.now().timestamp())
        if abs(now - iat) > (MIN_IAT_MIN * 60):
            raise ValueError('iat MUST be in the last ' + str(MIN_IAT_MIN) + ' minutes')
    

class JwtClientAssertionStructureSpid(JwtClientAssertionStructure):
    aud: HttpUrl


class JwtClientAssertionStructureCie(JwtClientAssertionStructure):
    aud: List[HttpUrl]
