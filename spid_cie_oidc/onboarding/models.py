from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.entity.validators import validate_public_jwks


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

    public_jwks = models.JSONField(
        blank=False,
        help_text=_("Public jwks of the Entities"),
        default=list,
        validators=[validate_public_jwks],
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
