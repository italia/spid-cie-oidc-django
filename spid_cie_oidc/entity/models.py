from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone

from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.entity.jwks import (
    create_jwk,
    serialize_rsa_key,
    private_pem_from_jwk,
    public_pem_from_jwk
)
from cryptojwt.jwk.jwk import key_from_jwk_dict

import datetime
import json
import uuid


ENTITY_TYPE_LEAFS = [
    "openid_relying_party",
    "openid_provider",
    "oauth_resource"
]

ENTITY_TYPES = ["federation_entity"] + ENTITY_TYPE_LEAFS

ENTITY_STATUS = {
    "unreachable": False,
    "valid": True,
    "signature_failed": False,
    "not_valid": False,
    "unknown": None,
    "expired": None
}


def is_leaf(statement_metadata):
    for _typ in ENTITY_TYPE_LEAFS:
        if _typ in statement_metadata:
            return True


class FederationEntityConfiguration(TimeStampedModel):
    """
        Federation Authority configuration.
    """
    def validate_entity_metadata(value):
        status = False
        for i in ENTITY_TYPES:
            if i in value:
                status = True
        if not status:
            raise ValidationError(
                _(f'Need to specify one of {", ".join(ENTITY_TYPES)}')
            )
    
    def _create_jwks():
        return [create_jwk()]

    uuid = models.UUIDField(
        blank=False, null=False, default=uuid.uuid4, unique=True,
        editable=False
    )
    sub = models.URLField(
        max_length=255,
        blank=False,
        null=False,
        help_text=_(
            "URL that identifies this Entity in the Federation. "
            "This value and iss are the same in the Entity Configuration."
        )
    )
    default_exp = models.PositiveIntegerField(
        default=33,
        help_text=_(
            "how many minutes from now() an issued statement must expire"
        )
    )
    default_signature_alg = models.CharField(
        max_length=16,
        default="RS256",
        blank=False,
        null=False,
        help_text=_("default signature algorithm, eg: RS256"),
    )
    authority_hints = models.JSONField(
        blank=True,
        null=False,
        help_text=_("only required if this Entity is an intermediary"),
        default=list,
    )
    jwks = models.JSONField(
        blank=False,
        null=False,
        help_text=_("a list of public keys"),
        default=_create_jwks,
    )
    trust_marks = models.JSONField(
        blank=True,
        help_text=_(
            "which trust marks MUST be exposed in its entity configuration"
        ),
        default=list,
    )
    trust_marks_issuers = models.JSONField(
        blank=True,
        help_text=_(
            "Only usable for Trust Anchors and intermediates. "
            "Which issuers are allowed to issue trust marks for the descendants. "
            'Example: {"https://www.spid.gov.it/certification/rp": '
            '["https://registry.spid.agid.gov.it", "https://intermediary.spid.it"],'
            '"https://sgd.aa.it/onboarding": ["https://sgd.aa.it", ]}'
        ),
        default=dict,
    )
    metadata = models.JSONField(
        blank=False,
        null=False,
        help_text=_(
            'federation_entity metadata, eg: '
            '{"federation_entity": { ... },'
            '"openid_provider": { ... },'
            '"openid_relying_party": { ... },'
            '"oauth_resource": { ... }'
            '}'
        ),
        default=dict,
        validators=[validate_entity_metadata,]
    )

    is_active = models.BooleanField(
        default=False, help_text=_(
            "If this configuration is active. "
            "At least one configuration must be active"
        )
    )

    class Meta:
        verbose_name = "Federation Entity Configuration"
        verbose_name_plural = "Federation Entity Configurations"

    @classmethod
    def get_active_conf(cls):
        """
        returns the first available active acsia engine configuration found
        """
        return cls.objects.filter(is_active=True).first()

    @property
    def public_jwks(self):
        res = []
        for i in self.jwks:
            skey = serialize_rsa_key(key_from_jwk_dict(i).public_key())
            skey['kid'] = i['kid']
            res.append(skey)
        return res

    @property
    def pems(self):
        res = {}
        for i in self.jwks:
            res[i["kid"]] = {
                "public": private_pem_from_jwk(i),
                "private": public_pem_from_jwk(i)
            }
        return json.dumps(res, indent=2)

    @property
    def kids(self):
        return [i['kid'] for i in self.jwks]

    @property
    def is_leaf(self):
        return is_leaf(self.metadata)
    
    @property
    def raw_entity_configuration(self):
        _now = timezone.localtime()
        conf = {
          "exp": int(
            (_now + datetime.timedelta(minutes = self.default_exp)
          ).timestamp()),
          "iat": int(_now.timestamp()),
          "iss": self.sub,
          "sub": self.sub,
          "jwks": self.public_jwks,
          "metadata": self.metadata
        }

        if self.trust_marks_issuers:
            conf['trust_marks_issuers'] = self.trust_marks_issuers

        if self.is_leaf:
            if self.authority_hints:
                conf['authority_hints'] = self.authority_hints
            else:
                _msg = f'Entity {self.sub} is a leaf and requires authority_hints valued'
                logger.error(_msg)
                messages.add_message(request, messages.ERROR, _msg)

        return conf
        
    @property
    def entity_configuration(self):
        return json.dumps(self.raw_entity_configuration, indent=2)

    def __str__(self):
        return "{} [{}]".format(
            self.sub, "active" if self.is_active else "--"
        )


class TrustChain(TimeStampedModel):
    """
        Federation Trust Chain
    """
    sub = models.URLField(
        max_length=255,
        blank=False,
        help_text=_(
            "URL that identifies this Entity in the Federation. "
        )
    )
    type = models.CharField(
        max_length=33,
        blank=True,
        default='openid_provider',
        choices = [(i,i) for i in ENTITY_TYPES],
        help_text=_("OpenID Connect Federation entity type")
    )
    exp = models.DateTimeField()
    iat = models.DateTimeField()
    chain = models.JSONField(
        blank=True,
        help_text=_(
            "A list of entity statements collected during the metadata discovery"
        ),
        default=list,
    )
    resultant_metadata = models.JSONField(
        blank=False,
        null=False,
        help_text=_(
            "The final metadata applied with the metadata policy built over the chain"
        ),
        default=dict,
    )
    parties_involved = models.JSONField(
        blank=True,
        help_text=_("subjects involved in the metadata discovery"),
        default=list,
    )
    status = models.CharField(
        max_length=33,
        default=False,
        help_text=_(
            "Status of this trust chain, on each update."
        ),
        choices = [(i, i) for i in ENTITY_STATUS.keys()]
    )
    status_log = models.JSONField(
        blank=True,
        help_text=_("status log"),
        default=dict,
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "If you need to disable the trust to this subject, deacticate this"
        )
    )

    class Meta:
        verbose_name = "Trust Chain"
        verbose_name_plural = "Trust Chains"
        unique_together = (('sub', 'type'))

    @property
    def is_valid(self):
        return self.is_active and ENTITY_STATUS[self.status]
    
    def __str__(self):
        return "{} [{}] [{}]".format(
            self.sub, self.type, self.is_valid
        )
