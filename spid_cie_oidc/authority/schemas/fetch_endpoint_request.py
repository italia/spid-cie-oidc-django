
from typing import Literal, Optional

from pydantic import BaseModel, HttpUrl, constr


class FetchRequest(BaseModel):
    # OpenID Federation 8.1.1: sub REQUIRED; issuer implied by fetch endpoint URL
    sub: HttpUrl

    def example():  # pragma: no cover
        return FetchRequest(sub="http://127.0.0.1:8000/oidc/rp")


class FetchResponse(BaseModel):
    jose : constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722


class FedAPIErrorResponse(BaseModel):
    operation: Optional[str]
    error: Literal[
        "invalid_request",
        "invalid_client",
        "invalid_issuer",
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
