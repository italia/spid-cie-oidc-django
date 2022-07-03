from typing import Literal

from pydantic import BaseModel


class IntrospectionResponse(BaseModel):
    active: bool
    # scope: Optional[List[str]]
    # sub: Optional[str]
    # exp: Optional[int]
    # client_id: HttpUrl
    # iss: Optional[HttpUrl]
    # TODO: migliorare: array di url con almeno uno
    # aud: Optional[List[HttpUrl]]


class IntrospectionErrorResponse(BaseModel):
    error_description: str


class IntrospectionErrorResponseSpid(IntrospectionErrorResponse):
    error: Literal[
        "invalid_client", "invalid_request", "server_error", "temporarily_unavailable"
    ]


class IntrospectionErrorResponseCie(IntrospectionErrorResponse):
    error: Literal[
        "invalid_client",
        "invalid_request",
        "invalid_token",
        "server_error",
        "temporarily_unavailable",
    ]
