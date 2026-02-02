
from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl, constr


class ResolveResponse(BaseModel):
    jose: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+")  # noqa: F722


class ResolveErrorResponse(BaseModel):
    operation: Optional[str]
    error: Literal[
        "invalid_request",
        "invalid_subject",
        "invalid_trust_anchor",
        "invalid_trust_chain",
        "invalid_metadata",
        "not_found",
        "server_error",
        "temporarily_unavailable",
        "unsupported_parameter",
    ]
    error_description: str


class ResolveRequest(BaseModel):
    sub: HttpUrl
    trust_anchor: HttpUrl
    # OpenID Federation 8.3.1: entity_type OPTIONAL, may occur multiple times
    entity_type: Optional[List[str]] = None
    format: Optional[Literal["json", "jose"]] = None

    def example():  # pragma: no cover
        return ResolveRequest(
            sub="http://127.0.0.1:8000/oidc/rp",
            trust_anchor="http://127.0.0.1:8000",
            format="json",
        )


#  class ResolveResponse(BaseModel):
    #  iss : HttpUrl
    #  sub : HttpUrl
    #  iat : int
    #  exp: int
    #  trust_marks : Json
    #  metadata: Json
    #  trust_chain: List


class ResolveHeader(BaseModel):
    Authorization : Optional[str]
