from django.utils import timezone
from django.utils.timezone import make_aware
import datetime


def iat_now() -> int:
    return int(datetime.datetime.now().timestamp())


def exp_from_now(minutes: int = 33) -> int:
    _now = timezone.localtime()
    return int((_now + datetime.timedelta(minutes=minutes)).timestamp())


def datetime_from_timestamp(value) -> datetime.datetime:
    return make_aware(datetime.datetime.fromtimestamp(value))
