from typing import List

from pydantic import BaseModel, HttpUrl, EmailStr


class FAMetadata(BaseModel):
    contacts: List[EmailStr]
    federation_fetch_endpoint: HttpUrl
    federation_resolve_endpoint: HttpUrl
    federation_list_endpoint: HttpUrl
    homepage_uri: HttpUrl
    organization_name: str
