from django.contrib import admin
from django.utils.safestring import mark_safe

# from prettyjson import PrettyJSONWidget


from .models import (
    FederationEntityConfiguration,
    FetchedEntityStatement,
    TrustChain
)


@admin.register(FederationEntityConfiguration)
class FederationEntityConfigurationAdmin(admin.ModelAdmin):
    # formfield_overrides = {
    # JSONField: {
    # "widget": PrettyJSONWidget(
    # attrs={"initial": "parsed", "disabled": True}
    # )
    # }
    # }
    list_display = (
        "sub",
        "type",
        "kids",
        "is_active",
        "created",
    )
    list_filter = ("created", "modified", "is_active")
    # search_fields = ('command__name',)
    readonly_fields = (
        "created",
        "modified",
        "entity_configuration_as_json",
        "pems_as_html",
        "kids",
        "type",
    )

    def pems_as_html(self, obj):
        res = ""
        data = dict()
        for k, v in obj.pems_as_dict.items():
            data[k] = {}
            for i in ("public", "private"):
                data[k][i] = v[i].replace("\n", "<br>")
            res += (
                f"<b>{k}</b><br><br>"
                f"{data[k]['public']}<br>"
                f"{data[k]['private']}<br><hr>"
            )
        return mark_safe(res)  # nosec


@admin.register(TrustChain)
class TrustChainAdmin(admin.ModelAdmin):
    list_display = ("sub", "type", "exp", "modified", "is_valid")
    list_filter = ("exp", "modified", "is_active", "type")
    search_fields = ("sub",)
    readonly_fields = (
        "created",
        "modified",
        "parties_involved",
        "metadata",
        "status",
        "log",
        "chain",
        "iat",
    )


@admin.register(FetchedEntityStatement)
class FetchedEntityStatementAdmin(admin.ModelAdmin):
    list_display = ("sub", "iss", "exp", "iat", "created", "modified")
    list_filter = ("created", "modified", "exp", "iat")
    search_fields = ("sub", "iss")
    readonly_fields = ("sub", "statement", "created", "modified", "iat", "exp", "iss")
