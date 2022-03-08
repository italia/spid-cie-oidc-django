from django.urls import path

from .views import (
    oidc_rp_landing,
    oidc_rpinitiated_logout,
    SpidCieOidcRpBeginView,
    SpidCieOidcRpCallbackEchoAttributes,
    SpidCieOidcRpCallbackView,
)

urlpatterns = []
urlpatterns += (
    path(
        "oidc/rp/authorization",
        SpidCieOidcRpBeginView.as_view(),
        name="spid_cie_rp_begin",
    ),
)
urlpatterns += (
    path(
        "oidc/rp/callback",
        SpidCieOidcRpCallbackView.as_view(),
        name="spid_cie_rp_callback",
    ),
)
urlpatterns += (
    path(
        "oidc/rp/echo_attributes",
        SpidCieOidcRpCallbackEchoAttributes.as_view(),
        name="spid_cie_rp_echo_attributes",
    ),
)

urlpatterns += (
    path("oidc/rp/landing", oidc_rp_landing, name="spid_cie_rp_landing"),
    path("oidc/rp/logout", oidc_rpinitiated_logout, name="spid_cie_rpinitiated_logout"),
)
