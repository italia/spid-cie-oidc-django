from django.contrib import admin
# from prettyjson import PrettyJSONWidget

from .models import FederationEntityConfiguration


@admin.register(FederationEntityConfiguration)
class FederationEntityConfigurationAdmin(admin.ModelAdmin):
    # formfield_overrides = {
    # JSONField: {
    # "widget": PrettyJSONWidget(
    # attrs={"initial": "parsed", "disabled": True}
    # )
    # }
    # }
    list_display = ('sub', 'created', 'kids', 'verify_https_cert', 'is_active')
    list_filter = ('created', 'modified', 'is_active')
    # search_fields = ('command__name',)
    readonly_fields = (
        "created", "modified", "entity_configuration", "pems", "kids"
    )
