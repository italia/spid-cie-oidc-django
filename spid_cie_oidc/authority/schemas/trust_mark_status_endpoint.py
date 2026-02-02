
from typing import Literal, Optional

from pydantic import BaseModel, HttpUrl, constr

# JWT pattern (three base64url segments) to avoid flake8 F722 on constr(regex=...)
_JWT_PATTERN = r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+"


class TrustMarkRequest(BaseModel):
    # Draft 48: trust_mark (JWT) REQUIRED for new flow
    trust_mark: Optional[constr(regex=_JWT_PATTERN)]
    # Retrocompat: sub + trust_mark_id / trust_mark_type / id
    sub: Optional[HttpUrl]
    trust_mark_id: Optional[HttpUrl]
    trust_mark_type: Optional[HttpUrl]
    id: Optional[HttpUrl]

    def example():  # pragma: no cover
        return TrustMarkRequest(
            trust_mark_type="https://www.spid.gov.it/openid-federation/agreement/op-public/",
            sub="http://127.0.0.1:8000/oidc/op",
        )


class TrustMarkResponse(BaseModel):
    active: bool


# OpenID Federation 8.4.2: Trust Mark Status Response JWT claims
class TrustMarkStatusResponsePayload(BaseModel):
    iss: str  # Entity Identifier of the issuer (Trust Mark Issuer)
    iat: int
    trust_mark: str  # The Trust Mark JWT this status is about
    status: Literal["active", "expired", "revoked", "invalid"]
