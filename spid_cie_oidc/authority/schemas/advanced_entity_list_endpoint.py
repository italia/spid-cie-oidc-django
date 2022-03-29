
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Json


class AdvancedEntityListRequest(BaseModel):
    page : Optional[int]

class AdvancedEntityListResponse(BaseModel):
    iss: HttpUrl
    iat: int
    entities: List[Json]
    page: int
    total_pages: int
    total_entries: int
    next_page_path: str
    prev_page_path: str
