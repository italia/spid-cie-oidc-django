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
    fetch, 
    entity_list, 
    onboarding_landing, 
    onboarding_registration, 
    onboarding_entities
)

_PREF = getattr(settings, "OIDC_PREFIX", "")

urlpatterns = [
    path(f"{_PREF}fetch/", fetch, name="oidcfed_fetch"),
    path(f"{_PREF}list/", entity_list, name="oidcfed_list"),
    path(f"{_PREF}onboarding/demo/", onboarding_landing, name="oidc_onboarding_demo"),
    path(f"{_PREF}onboarding/registration/", onboarding_registration, name="oidc_onboarding_registration"),
    path(f"{_PREF}onboarding/entities/", onboarding_entities, name="oidc_onboarding_entities"),
]
