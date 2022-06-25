from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


class RevocationRequest(BaseModel):
    client_assertion: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722
    client_assertion_type: Literal[
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]
    client_id: HttpUrl
    token: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722
