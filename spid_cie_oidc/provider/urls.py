from django.conf import settings
from django.urls import path

from .views import AuthzRequestView

_PREF = getattr(settings, "OIDC_PREFIX", "")

urlpatterns = [
    path(
        f"{_PREF}provider/authnrequest/",
        AuthzRequestView.as_view(),
        name="oidc_provider_authnrequest",
    ),
]
