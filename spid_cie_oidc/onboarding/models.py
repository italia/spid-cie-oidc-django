from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.entity.validators import validate_public_jwks
from spid_cie_oidc.entity.models import ENTITY_TYPES


class OnBoardingRegistration(TimeStampedModel):

    organization_name = models.CharField(
        max_length=254, help_text=_("Organization Name. ")
    )

    url_entity = models.URLField(
        max_length=254,
        blank=False,
        null=False,
        unique=True,
        help_text=_("URL of the Entity."),
    )

    authn_buttons_page_url = models.URLField(
        max_length=254,
        blank=False,
        null=False,
        help_text=_("URL of the page where the SPID/CIE button is available."),
    )

    auth_request_url = models.CharField(
        max_length=254,
        blank=True,
        null= True,
        help_text=_("SPID/CIE authentication request trigger url."),
    )

    public_jwks = models.JSONField(
        blank=False,
        help_text=_("Public jwks of the Entities"),
        default=list,
        validators=[validate_public_jwks],
    )

    type = models.CharField(
        max_length=33,
        blank=True,
        default="openid_relying_party",
        choices=[(i, i) for i in ENTITY_TYPES],
        help_text=_("OpenID Connect Federation entity type"),
    )

    contact = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text=_("any kind of contact type, usually an email."),
    )

    status = models.CharField(
        max_length=33,
        choices=(
            ("onboarded", "onboarded"),
            ("failed", "failed"),
            ("processing", "processing"),
            ("acquired", "acquired"),
        ),
        default="acquired",
    )

    created_by = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "OnBoarding Registration"
        verbose_name_plural = "OnBoarding Registrations"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.organization_name} {self.url_entity}"
