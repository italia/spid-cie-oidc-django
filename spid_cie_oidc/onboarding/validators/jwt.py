import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, validator
from spid_cie_oidc.entity.utils import datetime_from_timestamp

try:
    import spid_cie_oidc.entity.settings as entity_settings
    from django.conf import settings
    from django.utils import timezone
    NOW = timezone.localtime()
    MAX_ACCEPTED_TIMEDIFF = getattr(settings, "MAX_ACCEPTED_TIMEDIFF", entity_settings.MAX_ACCEPTED_TIMEDIFF)
except:
    NOW = datetime.datetime.now()
    MAX_ACCEPTED_TIMEDIFF = 5


class JwtClientAssertionStructure(BaseModel):
    iss: HttpUrl
    sub: HttpUrl
    iat: int
    exp: int
    jti: str

    @validator("exp")
    def validate_exp(cls, exp):
        now = int(NOW.timestamp())
        if exp <= now:
            raise ValueError('exp MUST be in the future')

    @validator("iat")
    def validate_iat(cls, iat):
        dt_iat = datetime_from_timestamp(iat)
        delta = datetime.timedelta(minutes=MAX_ACCEPTED_TIMEDIFF)
        if abs((NOW - dt_iat).total_seconds()) > delta.total_seconds():
            raise ValueError(f'iat MUST be in the last {MAX_ACCEPTED_TIMEDIFF} minutes')


class JwtClientAssertionStructureSpid(JwtClientAssertionStructure):
    aud: HttpUrl


class JwtClientAssertionStructureCie(JwtClientAssertionStructure):
    aud: List[HttpUrl]
