from django.contrib import admin

from .models import FederationDescendant, FederationDescendantContact


class FederationDescendantContactAdminInline(admin.TabularInline):
    model = FederationDescendantContact
    extra = 0
    readonly_fields = ('created', 'modified')
    raw_id_fields = ('entity',)


@admin.register(FederationDescendant)
class FederationDescendantAdmin(admin.ModelAdmin):
    list_display = ('sub', 'type', 'status', 'is_active', 'created')
    list_filter = ('type', 'created', 'modified', 'is_active')
    search_fields = ('sub',)
    readonly_fields = (
        "created", "modified"
    )
    inlines = (FederationDescendantContactAdminInline, )
