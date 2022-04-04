from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class ListRequest(BaseModel):
    is_leaf : Optional[bool]
    type : Optional[Literal["openid_relying_party", "openid_provider", "oauth_resource", "federation_entity"]]

    def example():  # pragma: no cover
        return ListRequest(
            is_leaf= True,
            type= "openid_provider"
        )


class ListResponse(BaseModel):
    response: List[HttpUrl]
