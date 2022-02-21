from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


class OnBoardingRegistration (models.Model):

    organization_name = models.CharField(
        max_length=254,
        help_text=_("Organization Name. ")
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
        unique=True,
        help_text=_("URL of the page where the SPID/CIE button is available."),
    )

    public_jwks = models.JSONField(
        blank=False,
        help_text=_("Public jwks of the Entities"),
        default=dict,
    )

    created_by = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "OnBoarding Registration"
        verbose_name_plural = "OnBoarding Registrations"

    def __str__(self):
        return f"{self.organization_name} {self.url_entity}"
