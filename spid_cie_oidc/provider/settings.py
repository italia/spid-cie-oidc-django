import aiohttp
from django.conf import settings

HTTPC_PARAMS = getattr(
    settings,
    "HTTPC_PARAMS",
    {
        "connection": {"ssl": True},
        "session": {"timeout": aiohttp.ClientTimeout(total=4)},
    }
)
