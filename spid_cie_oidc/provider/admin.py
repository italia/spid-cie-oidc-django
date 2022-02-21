from django.contrib import admin

from . models import *


@admin.register(OidcSession)
class OidcSessionAdmin(admin.ModelAdmin):
    list_display = ("user_id", "client_id", "created", "revoked")
    list_filter = ("created", "revoked")
    search_fields = ("client_id", "user_id")
    readonly_fields = (
        "user_uid",
        "user",
        "client_id",
        "created",
        "revoked",
        "sub",
        "userinfo_claims",
        "user_id",
        "authz_request"
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
        "session"
    )
