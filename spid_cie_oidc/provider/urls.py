from django.conf import settings
from django.urls import path

from .views import (
    oidc_provider_not_consent,
    AuthzRequestView,
    ConsentPageView,
    IntrospectionEndpoint,
    RevocationEndpoint,
    TokenEndpoint,
    UserInfoEndpoint,
    StaffTestingPageView
)

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
    path(
        f"{_PREF}/revocation/",
        RevocationEndpoint.as_view(),
        name="end_session_endpoint",
    ),
    path(
        f"{_PREF}/intospection/",
        IntrospectionEndpoint.as_view(),
        name="introspection_endpoint",
    ),
    path(
        f"{_PREF}/notconsent/",
        oidc_provider_not_consent,
        name="oidc_provider_not_consent",
    ),
    path(
        f"{_PREF}/testing/",
        StaffTestingPageView.as_view(),
        name="oidc_provider_staff_testing",
    ),
]
