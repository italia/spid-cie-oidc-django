from django.urls import path

from .views.rp_begin import SpidCieOidcRpBeginView
from .views.rp_callback import SpidCieOidcRpCallbackView
from .views.rp_callback_echo_attributes import SpidCieOidcRpCallbackEchoAttributes
from .views.rp_initiated_logout import oidc_rpinitiated_logout
from .views.rp_landing import oidc_rp_landing

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
