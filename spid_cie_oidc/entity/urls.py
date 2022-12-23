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
    entity_configuration, 
    resolve_entity_statement
)

_PREF = getattr(settings, "OIDC_PREFIX", "")

urlpatterns = [
    path(
        f"{_PREF}.well-known/openid-federation",
        entity_configuration,
        name="entity_configuration",
    ),
    path(f"{_PREF}resolve/", resolve_entity_statement, name="oidcfed_resolve")
]
