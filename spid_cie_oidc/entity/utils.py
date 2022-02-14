from django.utils import timezone
import datetime


def iat_now() -> int:
    return int(datetime.datetime.now().timestamp())


def exp_from_now(minutes: int = 33) -> int:
    _now = timezone.localtime()
    return int((_now + datetime.timedelta(minutes=minutes)).timestamp())
