from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


class AuthenticationResponse(BaseModel):
    # TODO: is 1*VSCHAR
    code: str
    state: constr(min_length=32)


class AuthenticationResponseCie(AuthenticationResponse):
    iss: HttpUrl


class AuthenticationErrorResponse(BaseModel):
    error: Literal[
        "invalid_request",
        "unauthorized_client",
        "access_denied",
        "unsupported_response_type",
        "invalid_scope",
        "server_error",
        "temporarily_unavailable",
    ]
    error_description: str
    state: constr(min_length=32)


class AuthenticationErrorResponseCie(AuthenticationErrorResponse):
    iss: HttpUrl
