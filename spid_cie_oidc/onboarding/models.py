from django.db import models
from django.utils.translation import gettext as _

class OnBoardingRegistration (models.Model):

    organization_name = models.CharField(
        max_length=33,
        help_text=_("Organization Name. ")
    )

    url_entity = models.URLField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        help_text=_("URL of the Entity."),
    )

    authn_buttons_page_url = models.URLField(
        max_length=255,
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