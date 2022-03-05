from django.conf import settings
from django.urls import path

from .views import AuthzRequestView, ConsentPageView, TokenEndpoint, UserInfoEndpoint

_PREF = getattr(settings, "OIDC_PREFIX", "oidc/op")

urlpatterns = [
    path(
        f"{_PREF}/authorization/",
        AuthzRequestView.as_view(),
        name="oidc_provider_authnrequest",
    ),
    path(
        f"{_PREF}/consent/",
        ConsentPageView.as_view(),
        name="oidc_provider_consent",
    ),
    path(
        f"{_PREF}/token/",
        TokenEndpoint.as_view(),
        name="oidc_provider_token_endpoint",
    ),
    path(
        f"{_PREF}/userinfo/",
        UserInfoEndpoint.as_view(),
        name="oidc_provider_userinfo_endpoint",
    ),
]
