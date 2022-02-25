from django.conf import settings
from django.urls import path

from .views import authn_request

_PREF = getattr(settings, "OIDC_PREFIX", "")

urlpatterns = [
    path(
        f"{_PREF}provider/authnrequest/",
        authn_request,
        name="oidc_provider_authnrequest",
    ),
]
