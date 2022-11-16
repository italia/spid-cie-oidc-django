from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class ListRequest(BaseModel):
    entity_type : Optional[Literal["openid_relying_party", "openid_provider", "oauth_resource", "federation_entity"]]

    def example():  # pragma: no cover
        return ListRequest(
            entity_type= "openid_provider"
        )


class ListResponse(BaseModel):
    response: List[HttpUrl]
