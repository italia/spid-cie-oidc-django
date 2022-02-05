from django.contrib import admin
from django.db.models import JSONField
from prettyjson import PrettyJSONWidget

from .models import FederationAuthorityConfiguration


@admin.register(FederationAuthorityConfiguration)
class FederationAuthorityConfigurationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {
            "widget": PrettyJSONWidget(
                attrs={"initial": "parsed", "disabled": True}
            )
        }
    }
    list_display = ('sub', 'created', 'verify_https_cert', 'is_active')
    list_filter = ('created', 'is_active')
    # search_fields = ('command__name',)
    readonly_fields = (
        "created", "modified", "entity_configuration"
    )
