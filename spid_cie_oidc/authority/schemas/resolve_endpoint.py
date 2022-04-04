
from typing import Literal, Optional

from pydantic import BaseModel, HttpUrl, Json


class ResolveRequest(BaseModel):
    sub : HttpUrl
    anchor : HttpUrl
    iss: Optional[HttpUrl]
    format :Literal["json"]

    def example():  # pragma: no cover
        return ResolveRequest(
            sub= "http://127.0.0.1:8000/oidc/rp/",
            anchor= "http://127.0.0.1:8000/",
            iss= "http://127.0.0.1:8000/",
            format= "json",
        )


class ResolveResponse(BaseModel):
    iss : HttpUrl
    sub : HttpUrl
    iat : int
    exp: int
    trust_marks : Json
    metadata: Json


class ResolveHeader(BaseModel):
    Authorization : Optional[str]
