
from typing import Optional

from pydantic import BaseModel, HttpUrl, constr


class TrustMarkRequest(BaseModel):
    sub : Optional[HttpUrl]
    id : Optional[HttpUrl]
    trust_mark : constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722


class TrustMarkResponse(BaseModel):
    active : bool
