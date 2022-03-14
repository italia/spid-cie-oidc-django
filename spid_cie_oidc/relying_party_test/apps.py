from django.apps import AppConfig


class RelyingPartyTestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spid_cie_oidc.relying_party_test"
    verbose_name = "SPID/CIE OIDC Federation RP Tests"
    label = "spid_cie_oidc_relying_party_test"
