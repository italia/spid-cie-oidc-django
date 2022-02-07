from django.urls import path

from . views import (
    oidc_rpinitiated_logout,
    SpidCieOidcRpBeginView,
    SpidCieOidcRpCallbackEchoAttributes,
    SpidCieOidcRpCallbackView
)

urlpatterns = []
urlpatterns += path('oidc/rp/begin',
                    SpidCieOidcRpBeginView.as_view(),
                    name='spid_cie_rp_begin'),
urlpatterns += path('oidc/rp/callback',
                    SpidCieOidcRpCallbackView.as_view(),
                    name='spid_cie_rp_callback'),
urlpatterns += path('echo_attributes',
                    SpidCieOidcRpCallbackEchoAttributes.as_view(),
                    name='spid_cie_rp_echo_attributes'),
urlpatterns += path('oidc/rp/logout',
                    oidc_rpinitiated_logout,
                    name='spid_cie_rpinitiated_logout'),
