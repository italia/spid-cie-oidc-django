
from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl, constr


class FetchRequest(BaseModel):
    sub : HttpUrl
    iss : Optional[HttpUrl]
    aud: Optional[List[HttpUrl]]

    def example():  # pragma: no cover
        return FetchRequest(
            sub= "http://127.0.0.1:8000/oidc/rp/",
            iss= "http://127.0.0.1:8000/",
            aud=["https://idp.it/"]
        )


class FetchResponse(BaseModel):
    jose : constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722


class FedAPIErrorResponse(BaseModel):
    operation: Optional[str]
    error: Literal["invalid_request"]
    error_description: str
