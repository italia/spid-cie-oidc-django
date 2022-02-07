from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.entity.models import (
    ENTITY_TYPES,
    ENTITY_STATUS,
    FederationEntityConfiguration
)
from spid_cie_oidc.entity.trust_chain import trust_chain_builder

import logging
import uuid

logger = logging.getLogger(__name__)


class FederationDescendant(TimeStampedModel):
    """
        Federation OnBoarding entries.
    """
    
    def def_uid():
        return f"autouid-{uuid.uuid4()}"
    
    uid = models.CharField(
        max_length=1024,
        default=def_uid,
        unique=True,
        help_text=_(
            "an unique code that identifies this entry. "
            "For italian public service it may be the IPA code."
        ),
    )
    name = models.CharField(
        max_length=33,
        help_text=_(
            "human readable name of this entity. "
            "It may be a unit or organization name"
        ),
    )
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
            "Logged in users can modify only sub, contacts and jwks "
            "attributes, if they're owner of this entry. "
        ),
        blank=True
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


# signal on each save
def trust_chain_trigger(**kwargs):
    subject = kwargs['instance'].sub

    # onboarding uses the first available configuration of federation_entity
    fe = FederationEntityConfiguration.objects.filter(
        is_active=True,
    ).first()
    
    logger.info(
        f"Receiving trust chain evaluation signal for {subject}"
    )
    return trust_chain_builder(subject)
post_save.connect(trust_chain_trigger, sender=FederationDescendant)
#
