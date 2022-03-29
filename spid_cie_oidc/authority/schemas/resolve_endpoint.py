
from typing import Literal, Optional

from pydantic import BaseModel, HttpUrl, Json


class ResolveRequest(BaseModel):
    sub : HttpUrl
    anchor : HttpUrl
    iss: Optional[HttpUrl]
    format :Literal["json"]


class ResolveResponse(BaseModel):
    iss : HttpUrl
    sub : HttpUrl
    iat : int
    exp: int
    trust_marks : Json
    metadata: Json


class ResolveHeader(BaseModel):
    Authorization : Optional[str]
