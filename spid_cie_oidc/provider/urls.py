from django.conf import settings
from django.urls import path

from .views.authz_request_view import AuthzRequestView
from .views.userinfo_endpoint import UserInfoEndpoint
from spid_cie_oidc.entity.views import (
    openid_connect_jwks_uri,
    openid_connect_signed_jwks_uri
)
from .views.connect import openid_configuration
from .views.consent_page_view import (
    ConsentPageView,
    oidc_provider_not_consent,
    UserAccessHistoryView,
    RevokeSessionView,
)
from .views.token_endpoint import TokenEndpoint
from .views.revocation_endpoint import RevocationEndpoint
from .views.introspection_endpoint import IntrospectionEndpoint

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
        name="oidc_provider_end_session_endpoint",
    ),
    path(
        f"{_PREF}/introspection/",
        IntrospectionEndpoint.as_view(),
        name="oidc_provider_introspection_endpoint",
    ),
    path(
        f"{_PREF}/notconsent/",
        oidc_provider_not_consent,
        name="oidc_provider_not_consent",
    ),
    path(
        f"{_PREF}/history/",
        UserAccessHistoryView.as_view(),
        name="oidc_provider_access_history",
    ),
    path(
        f"{_PREF}/revoke/",
        RevokeSessionView.as_view(),
        name="oidc_provider_revoke_session",
    ),
    path(
        f"{_PREF}/.well-known/openid-configuration",
        openid_configuration,
        name="oidc_provider_openid_configuration",
    ),
    path(
        f"{_PREF}/<str:metadata_type>/jwks.json",
        openid_connect_jwks_uri,
        name="oidc_connect_jwks_uri",
    ),
    path(
        f"{_PREF}/<str:metadata_type>/jwks.jose",
        openid_connect_signed_jwks_uri,
        name="oidc_connect_signed_jwks_uri",
    ),
]
