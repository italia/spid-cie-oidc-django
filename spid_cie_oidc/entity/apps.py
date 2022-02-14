from django.apps import AppConfig


class SpidCieFederationEntityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spid_cie_oidc.entity"
    verbose_name = "SPID/CIE OIDC Federation Entity"
    label = "spid_cie_oidc_entity"
