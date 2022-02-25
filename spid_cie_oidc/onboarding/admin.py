from django.contrib import admin

from .models import OnBoardingRegistration


@admin.register(OnBoardingRegistration)
class OnBoardingRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "organization_name",
        "url_entity",
        "authn_buttons_page_url",
        "public_jwks",
    )
