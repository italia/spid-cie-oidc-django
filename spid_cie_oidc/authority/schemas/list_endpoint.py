from typing import Literal, Optional

from pydantic import BaseModel


class ListRequest(BaseModel):
    is_leaf : Optional[bool]
    type : Optional[Literal["openid_relying_party", "openid_provider", "oauth_resource", "federation_entity"]]
