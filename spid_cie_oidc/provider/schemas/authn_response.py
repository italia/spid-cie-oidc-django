from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


class AuthenticationResponse(BaseModel):
    # TODO: is 1*VSCHAR
    code: str
    state: constr(min_length=32)

    def example():  # pragma: no cover
        return AuthenticationResponse(  # nosec B106
            code= "usDwMnEzJPpG5oaV8x3j&",
            state= "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd",
        )


class AuthenticationResponseCie(AuthenticationResponse):
    iss: HttpUrl

    def example():  # pragma: no cover
        return AuthenticationResponse(  # nosec B106
            code= "usDwMnEzJPpG5oaV8x3j&",
            state= "fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd",
            iss= "https://idserver.servizicie.interno.gov.it",
        )


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
