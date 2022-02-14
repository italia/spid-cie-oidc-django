from django.apps import AppConfig


class SpidCieFederationRpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spid_cie_oidc.relying_party"
    verbose_name = "SPID/CIE OIDC Federation Relying Party"
    label = "spid_cie_oidc_relying_party"
