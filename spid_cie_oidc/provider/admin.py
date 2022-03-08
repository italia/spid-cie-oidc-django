from django.contrib import admin

from .models import IssuedToken, OidcSession


@admin.register(OidcSession)
class OidcSessionAdmin(admin.ModelAdmin):
    list_display = ("user_uid", "client_id", "created", "revoked")
    list_filter = ("created", "revoked")
    search_fields = ("client_id", "user_uid")
    readonly_fields = (
        "nonce",
        "auth_code",
        "user_uid",
        "user",
        "sid",
        "client_id",
        "created",
        "revoked",
        "user_uid",
        "authz_request",
    )


@admin.register(IssuedToken)
class IssuedTokenAdmin(admin.ModelAdmin):
    list_display = ("client_id", "user_uid", "created")
    list_filter = ("created",)
    search_fields = ("session__user_uid", "session__client_id")
    readonly_fields = (
        "access_token",
        "id_token",
        "refresh_token",
        "created",
        "session",
    )
