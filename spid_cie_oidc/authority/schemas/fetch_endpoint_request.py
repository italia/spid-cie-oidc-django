
from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class FetchRequest(BaseModel):
    sub : HttpUrl
    iss : Optional[HttpUrl]
    format : Optional[Literal["json"]]
    aud: Optional[List[HttpUrl]]
