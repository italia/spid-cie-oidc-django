from django.contrib import admin

from .models import RelyingPartyReport, RelyingPartyTest


@admin.register(RelyingPartyReport)
class RelyingPartyReportAdmin(admin.ModelAdmin):
    search_fields = ("client_id",)
    list_display = (
        "client_id", "status", "user", "created", "modified"
    )
    list_filter = ("created", "status")


@admin.register(RelyingPartyTest)
class RelyingPartyTestAdmin(admin.ModelAdmin):
    search_fields = ("name", "report__client_id")
    list_display = (
        "client_id", "status",
        "code", "http_status_code", "screenshot_as_html"
    )
    list_filter = ("created", "status")
    readonly_fileds = ("screenshot_as_html",)

    def screenshot_as_html(self, obj):
        return obj.screenshot # pragma: no cover

    screenshot_as_html.short_description = "Screenshot"
