from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.abstract_models import TimeStampedModel


ENTITY_TYPES = (
    "openid_relying_party",
    "openid_provider",
    "federation_entity",
    "oauth_resource"
)

ENTITY_STATUS = {
    "unreachable": False,
    "valid": True,
    "signature_failed": False,
    "not_valid": False,
    "unknown": None
}



class FederationDescendant(TimeStampedModel):
    """
        Federation OnBoarding entries.
    """
    sub = models.URLField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        help_text=_(
            "URL that identifies this Entity in the Federation."
        ),
    )
    type = models.CharField(
        max_length=33,
        blank=True,
        default='openid_relying_party',
        choices = [(i,i) for i in ENTITY_TYPES],
        help_text=_("OpenID Connect Federation entity type")
    )
    registrant = models.ManyToManyField(
        get_user_model(),
        help_text=_(
            "users that can login and modify sub, contacts and jwks"
        )
    )
    jwks = models.JSONField(
        blank=False,
        null=False,
        help_text=_("a list of public keys"),
        default=list
    )
    trust_marks = models.JSONField(
        blank=True,
        help_text=_(
            "trust marks released for this subject"
        ),
        default=list,
    )
    metadata_policy = models.JSONField(
        blank=True,
        help_text=_("if present overloads the DEFAULT policy"),
        default=dict,
    )
    constraints = models.JSONField(
        blank=True,
        help_text=_("if present overloads the DEFAULT policy"),
        default=dict,
    )
    extended_claims = models.JSONField(
        blank=True,
        help_text=_(
            "a dictionary containing any other claim like: "
            "jti, crti, policy_language_crit and any other extension"
        ),
        default=dict,
    )
    status = models.CharField(
        max_length=33,
        default=False,
        help_text=_(
            "Its entity configuration is periodically fetched and validated."
        ),
        choices = [(i, i) for i in ENTITY_STATUS.keys()]
    )
    status_log = models.JSONField(
        blank=True,
        help_text=_("status log"),
        default=dict,
    )
    is_active = models.BooleanField(
        default=False, help_text=_("If this entity is active. ")
    )

    class Meta:
        verbose_name = "Federation Entity Descendant"
        verbose_name_plural = "Federation Entity Descendants"

    def __str__(self):
        return "{} [{} and {}]".format(
            self.sub,
            self.status,
            "active" if self.is_active else "--"
        )


class FederationDescendantContact(TimeStampedModel):
    """
        Federation OnBoarding entries.
    """
    entity = models.ForeignKey(
        FederationDescendant,
        on_delete=models.CASCADE,
        help_text=_("Entity for which this contac is related")
    )
    contact = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text=_(
            "any kind of contact type, usually an email."
        ),
    )
    type = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        choices = [
            (i, i) for i in ('email', 'telephone', 'other')
        ]
    )

    class Meta:
        verbose_name = "Federation Entity Contact"
        verbose_name_plural = "Federation Entity Contacts"

    def __str__(self):
        return f"{self.contact} {self.entity.sub}"
