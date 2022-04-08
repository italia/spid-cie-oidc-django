from django.contrib import admin
from django.contrib import messages
from django.db import IntegrityError

from .models import OnBoardingRegistration
from spid_cie_oidc.authority.models import FederationDescendant, FederationDescendantContact


@admin.register(OnBoardingRegistration)
class OnBoardingRegistrationAdmin(admin.ModelAdmin):

    @admin.action(description='enable descendant')
    def enable_as_descendant(modeladmin, request, queryset):
        for entity_onboarded in queryset:
            name = entity_onboarded.organization_name
            sub = entity_onboarded.url_entity
            jwks = entity_onboarded.public_jwks
            _type = entity_onboarded.type
            contact = entity_onboarded.contact

            try:
                entity = FederationDescendant.objects.create(
                    name = name,
                    sub = sub,
                    type = _type,
                    jwks = jwks,
                    is_active = True,
                    status = "valid"
                )
                FederationDescendantContact.objects.create(
                    entity = entity,
                    contact = contact,
                    type = "email"
                )
                entity_onboarded.status = "onboarded"
                entity_onboarded.save()
            except IntegrityError: # pragma: no cover
                messages.error(request, f"Already exists a descendant with subject: {sub}")

    list_display = (
        "organization_name",
        "url_entity",
        "type",
        "authn_buttons_page_url",
        "public_jwks",
    )
    actions = [enable_as_descendant]
