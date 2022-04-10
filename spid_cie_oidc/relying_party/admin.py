import logging

from django.contrib import admin

from .models import OidcAuthentication, OidcAuthenticationToken
from .utils import html_json_preview

logger = logging.getLogger(__name__)


class OidcAuthenticationTokenInline(admin.StackedInline):
    model = OidcAuthenticationToken
    extra = 0
    max_num = 1
    readonly_fields = (
        "scope",
        "expires_in",
        "token_type",
        "code",
        "access_token",
        "id_token",
        "refresh_token",
        "access_token_preview",
        "id_token_preview",
    )


@admin.register(OidcAuthentication)
class OidcAuthenticationAdmin(admin.ModelAdmin):
    search_fields = ("endpoint", "state", "client_id", )
    list_display = ("client_id", "state", "endpoint", "created", "modified")
    list_filter = ("created", "endpoint")
    inlines = (OidcAuthenticationTokenInline,)
    readonly_fields = (
        "client_id",
        "state",
        "endpoint",
        "successful",
        "json_preview",
        "provider_configuration",
        "created",
        "modified",
    )
    exclude = ("issuer_id", "data", "provider_configuration", "provider_jwks")
    fieldsets = (
        (None, {"fields": ("provider_id", "client_id", "state", "endpoint")}),
        (
            "Status",
            {
                "fields": (
                    "successful",
                    "created",
                    "modified",
                )
            },
        ),
        (
            "Authorization request previews",
            {
                "fields": (
                    "json_preview",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Provider Discovery result",
            {
                "fields": ("provider_configuration",),
                "classes": ("collapse",),
            },
        ),
    )

    def json_preview(self, obj): # pragma: no cover
        return html_json_preview(obj.data)

    json_preview.short_description = "Authentication Request data"
