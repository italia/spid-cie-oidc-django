from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class IntrospectionResponse(BaseModel):
    active: bool
    scope: Optional[List[str]]
    sub: Optional[str]
    exp: Optional[int]
    client_id: HttpUrl
    iss: Optional[HttpUrl]
    # TODO: migliorare: array di url con almeno uno
    aud: Optional[List[HttpUrl]]
