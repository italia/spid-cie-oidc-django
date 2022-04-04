
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Json


class AdvancedEntityListRequest(BaseModel):
    page : Optional[int]

    def example():  # pragma: no cover
        return AdvancedEntityListRequest(
            page= 1,
        )


class AdvancedEntityListResponse(BaseModel):
    iss: HttpUrl
    iat: int
    entities: List[Json]
    page: int
    total_pages: int
    total_entries: int
    next_page_path: str
    prev_page_path: str

    def example():  # pragma: no cover
        return AdvancedEntityListResponse(
            iss= "https://registry.spid.gov.it/",
            iat= 1620050972,
            entities= [
                # "{'https://rp.example.it/spid/': {'iat': 1588455866} }",
                # "{'https://rp.another.it/spid/': {'iat': 1588455866} }"
            ],
            page= 1,
            total_pages= 2,
            total_entries= 189,
            next_page_path= "/federation_adv_list/?page=2",
            prev_page_path= ""
        )
