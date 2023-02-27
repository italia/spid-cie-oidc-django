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

from .views import entity_list, fetch, trust_mark_status, advanced_entity_listing

_PREF = getattr(settings, "OIDC_PREFIX", "")
urlpatterns = [
    path(f"{_PREF}fetch/", fetch, name="oidcfed_fetch"),
    path(f"{_PREF}list/", entity_list, name="oidcfed_list"),
    path(
        f"{_PREF}trust_mark_status/",
        trust_mark_status,
        name="oidcfed_trust_mark_status",
    ),
    path(
        f"{_PREF}advanced_entity_listing/",
        advanced_entity_listing,
        name="oidcfed_advanced_entity_listing",
    ),
]
