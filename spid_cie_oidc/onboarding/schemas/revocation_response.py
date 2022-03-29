from typing import Literal

from pydantic import BaseModel


class RevocationErrorResponse(BaseModel):
    error: Literal[
        "invalid_request",
        "invalid_client",
        "unauthorized_client",
        "invalid_scope",
        "unsupported_token_type",
    ]
    error_description: str
