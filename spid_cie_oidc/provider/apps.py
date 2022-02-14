from django.apps import AppConfig


class SpidCieOidcOpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spid_cie_oidc.provider"
    verbose_name = "SPID/CIE OIDC Federation Provider"
    label = "spid_cie_oidc_provider"
