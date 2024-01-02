from spid_cie_oidc.entity.utils import iat_now

from pydantic import BaseModel, AnyHttpUrl, constr, validator
from typing import Literal, Optional, List


class ClientAssertion(BaseModel):
    iss: AnyHttpUrl
    sub: AnyHttpUrl
    iat: int
    exp: int
    jti: Optional[str]
    aud: str | List[AnyHttpUrl]

    @validator("sub")
    def iss_and_sub_must_match(cls, sub, values):
        if values['iss'] != sub:
            raise ValueError(
                'Client Assertion: iss and sub must have the same value'
            )
        return sub

    @validator("exp")
    def not_expired(cls, exp, values):
        _now = iat_now()
        if not (values['iat'] <= _now < exp):
            raise ValueError(
                'Client Assertion: exp must be greater than '
                'iat and less than the current time.'
                f'{values["iat"]} <= {_now} < {exp}'
            )
        return exp
