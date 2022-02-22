from django.apps import AppConfig


class AuthorityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spid_cie_oidc.authority"
    verbose_name = "SPID/CIE OIDC Federation Authority"
    label = "spid_cie_oidc_authority"
