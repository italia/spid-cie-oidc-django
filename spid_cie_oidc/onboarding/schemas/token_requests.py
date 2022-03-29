from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


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
        return TokenAuthnCodeRequest(  
            client_id = "http://example.com",  
            client_assertion = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVS...__Q5idQ", # nosec B106
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  
            code = "bb03ad1f2e838335c1050ae280a64f4e195dbeb17ba8aa2dc6fd99e1c5181fc735be6af10b...80af5", # nosec B106
            code_verifier = "nd6gJEXzUZApV46u4DmVUfZgBYc2SJsZGkaBftof4gcI95ByALg",
            grant_type = "authorization_code"  # nosec B106
        )


class TokenRefreshRequest(TokenRequest):
    grant_type: Literal["refresh_token"]
    refresh_token: str

    def example():
        return TokenRefreshRequest( 
            client_id = "http://example.com",  
            client_assertion = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVSjNBeHdHR3pfOTh1UkZ...__Q5idQ",# nosec B106
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  
            refresh_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRCNjdnTDdjazNURmlJQWY3TjZfN1NIdnFrME1EWU1FUWNvR0dsa1...BH9VAA", # nosec B106
            grant_type = "refresh_token" # nosec B106
        )
