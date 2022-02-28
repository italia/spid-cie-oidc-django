

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, validator
from .jwks import JwksCie, JwksSpid


class GrantTypeSupported(str, Enum):
    refresh_token = "refresh_token" # nosec - B105
    authorization_code = "authorization_code"


class RpMetadata(BaseModel):
    redirect_uris: List[HttpUrl]
    response_types = ["code"]
    grant_types: List[GrantTypeSupported]
    client_id: HttpUrl
    # TODO: Could be specified in multiple languages
    client_name: str


class RpMetadataSpid(RpMetadata):
    jwks_uri: HttpUrl
    jwks:Optional[JwksSpid]

    @validator("jwks")
    def validate_jwks_uri(cls, jwks, values):
        jwks_uri = values.get("jwks_uri")
        if (jwks_uri and jwks):
            raise ValueError('jwks MUST NOT indicate')


class RpMetadataCie(RpMetadata):
    jwks_uri: HttpUrl
    jwks:Optional[JwksCie]
    application_type = "web"
    tls_client_certificate_bound_access_tokens: Optional[bool]

    @validator("jwks")
    def validate_jwks_uri(cls, jwks, values):
        jwks_uri = values.get("jwks_uri")
        if (jwks_uri and jwks):
            raise ValueError('jwks MUST NOT indicate')
