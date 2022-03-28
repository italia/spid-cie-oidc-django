from django import template
from django.conf import settings


from spid_cie_oidc.provider.settings import (
    OIDCFED_PROVIDER_PROFILES_MEDIA,
    OIDCFED_DEFAULT_PROVIDER_PROFILE
)

register = template.Library()


@register.simple_tag
def oidc_provider_logo():
    return f"""{settings.STATIC_URL}{OIDCFED_PROVIDER_PROFILES_MEDIA.get(
        OIDCFED_DEFAULT_PROVIDER_PROFILE, {}
    ).get('logo', "")}"""


@register.simple_tag
def oidc_provider_arc_value_position():
    return f"""{OIDCFED_PROVIDER_PROFILES_MEDIA.get(
        OIDCFED_DEFAULT_PROVIDER_PROFILE, {}
    ).get('arc_position', "")}"""
