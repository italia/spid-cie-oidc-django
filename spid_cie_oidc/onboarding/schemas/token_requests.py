from typing import Literal

from pydantic import BaseModel, HttpUrl, constr

from spid_cie_oidc.onboarding.tests.token_request_settings import TOKEN_AUTHN_CODE_REQUEST


class TokenRequest(BaseModel):
    client_id: HttpUrl
    client_assertion: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722
    client_assertion_type: Literal[
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]


class TokenAuthnCodeRequest(TokenRequest):
    # TODO: is 1*VSCHAR
    code: str
    # TODO: is 43*128unreserved, where unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
    code_verifier: str
    grant_type: Literal["authorization_code"]

    def example():
        return TokenAuthnCodeRequest( # noqa: E722
            client_id = "http://example.com",  # noqa: E722
            client_assertion = "string.string.string", # noqa: E722
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  # noqa: E722
            code = "string", # noqa: E722
            code_verifier = "string", # noqa: E722
            grant_type = "authorization_code"  # noqa: E722
        )


class TokenRefreshRequest(TokenRequest):
    grant_type: Literal["refresh_token"]
    refresh_token: str

    def example():
        return TokenRefreshRequest(  # noqa: E722
            client_id = "http://example.com",  # noqa: E722
            client_assertion = "string.string.string", # noqa: E722
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  # noqa: E722
            refresh_token = "string", # noqa: E722
            grant_type = "refresh_token" # noqa: E722
        )
