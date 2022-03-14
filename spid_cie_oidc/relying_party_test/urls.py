from django.conf import settings
from django.urls import path

from .views import (
    StaffTestingPageView
)

_PREF = getattr(settings, "OIDC_PREFIX", "oidc/op/rp-test/")

urlpatterns = [

    path(
        f"{_PREF}landing/",
        StaffTestingPageView.as_view(),
        name="oidc_provider_staff_testing",
    ),

]
