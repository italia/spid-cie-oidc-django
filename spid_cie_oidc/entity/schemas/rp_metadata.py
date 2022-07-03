from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, root_validator
from .jwks import JwksSpid


class GrantTypeSupported(str, Enum):
    refresh_token = "refresh_token"  # nosec - B105
    authorization_code = "authorization_code"


class RPMetadata(BaseModel):
    organization_name: str
    redirect_uris: List[HttpUrl]
    response_types = ["code"]
    grant_types: List[GrantTypeSupported]
    client_id: HttpUrl
    # TODO: Could be specified in multiple languages
    client_name: str

    signed_jwks_uri: Optional[HttpUrl]
    jwks_uri: Optional[HttpUrl]
    jwks: Optional[JwksSpid]

    @root_validator(pre=False)
    def validate(cls, values):
        jwks = values.get("jwks")
        jwks_uri = values.get("jwks_uri")
        signed_jwks_uri = values.get("signed_jwks_uri")
        if not jwks_uri and not jwks and not signed_jwks_uri:
            raise ValueError(
                "one of signed_jwks_uri or jwks_uri or jwks must be set"
            )
        if jwks_uri and jwks:
            raise ValueError("can't use jwks and jwks_uri together")
        elif jwks_uri and signed_jwks_uri:
            raise ValueError(
                "can't use signed_jwks_uri and jwks_uri together"
            )
        return values


class RPMetadataSpid(RPMetadata):
    pass


class RPMetadataCie(RPMetadataSpid):
    application_type = "web"
    tls_client_certificate_bound_access_tokens: Optional[bool]
