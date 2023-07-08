from django.urls import path

from spid_cie_oidc.entity.views import (
    openid_connect_jwks_uri,
    openid_connect_signed_jwks_uri
)
from .views.rp_begin import SpidCieOidcRpBeginView
from .views.rp_callback import SpidCieOidcRpCallbackView
from .views.rp_extend_session import SpidCieOidcRefreshToken
from .views.rp_callback_echo_attributes import SpidCieOidcRpCallbackEchoAttributes
from .views.rp_initiated_logout import SpidCieOidcRpLogout  # oidc_rpinitiated_logout
from .views.rp_introspection import SpidCieOidcRpIntrospection
from .views.rp_landing import oidc_rp_landing
from django.contrib.auth.decorators import login_required
_PREF = "oidc/rp"

urlpatterns = []
urlpatterns += (
    path(
        f"{_PREF}/authorization",
        SpidCieOidcRpBeginView.as_view(),
        name="spid_cie_rp_begin",
    ),
)
urlpatterns += (
    path(
        f"{_PREF}/callback",
        SpidCieOidcRpCallbackView.as_view(),
        name="spid_cie_rp_callback",
    ),
)
urlpatterns += (
    path(
        f"{_PREF}/echo_attributes",
        SpidCieOidcRpCallbackEchoAttributes.as_view(),
        name="spid_cie_rp_echo_attributes",
    ),
)

urlpatterns += (
    path(
        f"{_PREF}/extend_session",
        login_required(SpidCieOidcRefreshToken.as_view()),
        name="spid_cie_rp_extend_session",
    ),
)


urlpatterns += (
    path(
        f"{_PREF}/introspection",
        login_required(SpidCieOidcRpIntrospection.as_view()),
        name="spid_cie_rp_echo_introspection",
    ),
)

urlpatterns += (
    path(
        f"{_PREF}/logout",
        login_required(SpidCieOidcRpLogout.as_view()),
        name="spid_cie_rpinitiated_logout",
    ),
)

urlpatterns += (
    path(f"{_PREF}/landing", oidc_rp_landing, name="spid_cie_rp_landing"),
    # path(f"{_PREF}/logout", oidc_rpinitiated_logout, name="spid_cie_rpinitiated_logout"),
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
)
