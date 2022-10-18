
from typing import Literal, Optional

from pydantic import BaseModel, HttpUrl, constr


class ResolveResponse(BaseModel):
    jose : constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722


class ResolveErrorResponse(BaseModel):
    operation: Optional[str]
    error: Literal["invalid_request"]
    error_description: str


class ResolveRequest(BaseModel):
    sub : HttpUrl
    anchor : HttpUrl
    format :Literal["json"]

    def example():  # pragma: no cover
        return ResolveRequest(
            sub= "http://127.0.0.1:8000/oidc/rp/",
            anchor= "http://127.0.0.1:8000/",
            format= "json",
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
