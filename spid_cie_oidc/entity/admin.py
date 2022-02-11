from django.contrib import admin
# from prettyjson import PrettyJSONWidget

from .models import FederationEntityConfiguration, TrustChain


@admin.register(FederationEntityConfiguration)
class FederationEntityConfigurationAdmin(admin.ModelAdmin):
    # formfield_overrides = {
    # JSONField: {
    # "widget": PrettyJSONWidget(
    # attrs={"initial": "parsed", "disabled": True}
    # )
    # }
    # }
    list_display = ('sub', 'type', 'kids', 'is_active', 'created',)
    list_filter = ('created', 'modified', 'is_active')
    # search_fields = ('command__name',)
    readonly_fields = (
        "created", "modified", "entity_configuration_as_json", "pems", "kids", "type"
    )


@admin.register(TrustChain)
class TrustChainAdmin(admin.ModelAdmin):
    list_display = ('sub', 'type', 'exp', 'modified', 'is_valid')
    list_filter = ('exp', 'modified', 'is_active', 'type')
    search_fields = ('sub',)
    readonly_fields = (
        "created", "modified", "parties_involved",
        "resultant_metadata", "type", "status", "status_log", "chain",
        "exp", "iat"
    )
