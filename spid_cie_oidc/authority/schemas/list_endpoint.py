from typing import List, Literal, Optional, Union

from pydantic import BaseModel, HttpUrl


class ListRequest(BaseModel):
    # OpenID Federation 8.2.1: optional filters
    entity_type: Optional[
        Literal["openid_relying_party", "openid_provider", "oauth_resource", "federation_entity"]
    ] = None
    trust_marked: Optional[bool] = None
    trust_mark_type: Optional[Union[HttpUrl, str]] = None
    intermediate: Optional[bool] = None

    def example():  # pragma: no cover
        return ListRequest(entity_type="openid_provider")


class ListResponse(BaseModel):
    response: List[HttpUrl]
