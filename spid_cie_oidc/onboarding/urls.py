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
    onboarding_convert_pem,
    onboarding_resolve_statement,
    onboarding_schemas_federation_entity_endpoints,
    onboarding_validating_trustmark,
    onboarding_decode_jwt,
    onboarding_apply_policy,
    onboarding_validate_md,
    onboarding_schemas_authorization,
    onboarding_schemas_introspection,
    onboarding_schemas_metadata,
    onboarding_schemas_revocation,
    onboarding_schemas_token,
    onboarding_schemas_jwt_client_assertion,
    onboarding_validate_authn_request,
    onboarding_validate_ec,
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
        f"{_PREF}onboarding/tools/create-jwk/",
        onboarding_create_jwk,
        name="oidc_onboarding_create_jwk",
    ),
    path(
        f"{_PREF}onboarding/tools/convert-jwk/",
        onboarding_convert_jwk,
        name="oidc_onboarding_convert_jwk",
    ),
    path(
        f"{_PREF}onboarding/convert-pem/",
        onboarding_convert_pem,
        name="oidc_onboarding_convert_pem",
    ),
    path(
        f"{_PREF}onboarding/tools/resolve-statement/",
        onboarding_resolve_statement,
        name="oidc_onboarding_resolve_statement",
    ),
    path(
        f"{_PREF}onboarding/tools/validating-trustmark",
        onboarding_validating_trustmark,
        name="oidc_onboarding_validating_trustmark",
    ),
    path(
        f"{_PREF}onboarding/tools/decode-jwt",
        onboarding_decode_jwt,
        name="oidc_onboarding_tools_decode_jwt",
    ),
    path(
        f"{_PREF}onboarding/tools/apply-policy",
        onboarding_apply_policy,
        name="oidc_onboarding_tools_apply_policy",
    ),
    path(
        f"{_PREF}onboarding/schemas/federation_entity",
        onboarding_schemas_federation_entity_endpoints,
        name="oidc_onboarding_schemas_federation_entity",
    ),
    path(
        f"{_PREF}onboarding/schemas/authorization",
        onboarding_schemas_authorization,
        name="oidc_onboarding_schemas_Authorization",
    ),
    path(
        f"{_PREF}onboarding/schemas/introspection",
        onboarding_schemas_introspection,
        name="oidc_onboarding_schemas_introspection",
    ),
    path(
        f"{_PREF}onboarding/schemas/metadata",
        onboarding_schemas_metadata,
        name="oidc_onboarding_schemas_metadata",
    ),
    path(
        f"{_PREF}onboarding/schemas/revocation",
        onboarding_schemas_revocation,
        name="oidc_onboarding_schemas_revocation",
    ),
    path(
        f"{_PREF}onboarding/schemas/token",
        onboarding_schemas_token,
        name="oidc_onboarding_schemas_token",
    ),
    path(
        f"{_PREF}onboarding/schemas/jwt/client/assertion",
        onboarding_schemas_jwt_client_assertion,
        name="oidc_onboarding_schemas_jwt_client_assertion",
    ),
    path(
        f"{_PREF}onboarding/tools/validate-md",
        onboarding_validate_md,
        name="oidc_onboarding_validate_md",
    ),
    path(
        f"{_PREF}onboarding/tools/validate-authn-request",
        onboarding_validate_authn_request,
        name="oidc_onboarding_validate_authn_request_jwt",
    ),
    path(
        f"{_PREF}onboarding/tools/validate-ec",
        onboarding_validate_ec,
        name="oidc_onboarding_validate_ec",
    ),
]
