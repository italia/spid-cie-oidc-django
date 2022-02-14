from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    name = "spid_cie_oidc.accounts"
    verbose_name = _("User accounts")
    default_auto_field = "django.db.models.BigAutoField"
    label = "spid_cie_oidc_accounts"
