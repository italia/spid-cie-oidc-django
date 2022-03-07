"""acsia_agent_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path

from .views import (
    onboarding_landing,
    onboarding_registration,
    onboarding_entities,
    onboarding_create_jwk,
    onboarding_convert_jwk,
    onboarding_resolve_statement,
    onboarding_validating_trustmark,
    onboarding_decode_jwt
)

_PREF = getattr(settings, "OIDC_PREFIX", "")

urlpatterns = [
    path(
        f"{_PREF}onboarding/landing/",
        onboarding_landing,
        name="oidc_onboarding_landing",
    ),
    path(
        f"{_PREF}onboarding/registration/",
        onboarding_registration,
        name="oidc_onboarding_registration",
    ),
    path(
        f"{_PREF}onboarding/entities/",
        onboarding_entities,
        name="oidc_onboarding_entities",
    ),
    path(
        f"{_PREF}onboarding/create-jwk/",
        onboarding_create_jwk,
        name="oidc_onboarding_create_jwk",
    ),
    path(
        f"{_PREF}onboarding/convert-jwk/",
        onboarding_convert_jwk,
        name="oidc_onboarding_convert_jwk",
    ),
    path(
        f"{_PREF}onboarding/resolve-statement/",
        onboarding_resolve_statement,
        name="oidc_onboarding_resolve_statement",
    ),
    path(
        f"{_PREF}onboarding/tools/validating-trustmark",
        onboarding_validating_trustmark,
        name="oidc_onboarding_tools_validating_trustmark",
    ),
    path(
        f"{_PREF}onboarding/tools/decode-jwt",
        onboarding_decode_jwt,
        name="oidc_onboarding_tools_decode_jwt",
    ),
]
