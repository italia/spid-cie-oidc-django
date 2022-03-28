import logging
from django import forms
from django.utils.translation import gettext_lazy as _
from spid_cie_oidc.entity.validators import validate_public_jwks
from spid_cie_oidc.authority.validators import validate_entity_configuration
from .validators import unique_entity_url
from spid_cie_oidc.entity.models import ENTITY_TYPES
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    OIDCFED_TRUST_ANCHORS = getattr(
        settings, "OIDCFED_TRUST_ANCHORS"
    )
except AttributeError: # pragma: no cover
    OIDCFED_TRUST_ANCHORS = []
    logger.warning(
        "OIDCFED_TRUST_ANCHORS not configured in your settings file."
    )


class OnboardingRegistrationForm(forms.Form):

    organization_name = forms.CharField(
        initial="",
        label=_("organization Name"),
        error_messages={"required": _("Enter your organization name")},
    )

    url_entity = forms.URLField(
        initial="",
        label=_("url of the entity"),
        error_messages={"required": _("Enter your url of the entity")},
        validators=[validate_entity_configuration, unique_entity_url],
    )

    authn_buttons_page_url = forms.URLField(
        initial="",
        label=_("url of the page where the SPID/CIE button is available"),
        error_messages={
            "required": _(
                "Enter the url of the page where the SPID/CIE button is available"
            )
        },
    )

    auth_request_url = forms.CharField(
        initial="",
        label=_("authentication request url"),
        required = False
    )

    contact = forms.EmailField(
        initial="",
        label=_("contact email"),
        error_messages={"required": _("Enter your contact email")},
    )

    type = forms.ChoiceField(
        choices=[(i, i) for i in ENTITY_TYPES],
        label="",
        error_messages={"required": _("Select a entity type")},
    )

    public_jwks = forms.JSONField(
        initial=list,
        label=_("public jwks of the entities"),
        error_messages={"required": _("Enter the public jwks of the entities")},
        validators=[validate_public_jwks],
    )


class OnboardingCreateTrustChain(forms.Form):

    sub = forms.URLField(
        initial="",
        label=_("url of subject"),
        error_messages={"required": _("Enter the subject")},
    )

    type = forms.ChoiceField(
        choices=[(i, i) for i in ENTITY_TYPES],
        label="OpenID Connect Federation entity type",
        error_messages={"required": _("Select a entity type")},
    )

    anchor = forms.ChoiceField(
        choices=[(i, i) for i in OIDCFED_TRUST_ANCHORS],
        label=_("url of the trust anchor"),
        error_messages={"required": _("Enter the url of trust anchor")},
    )


class OnboardingValidatingTrustMarkForm(forms.Form):

    sub = forms.URLField(
        initial="",
        label=_("Url of subject"),
        required=False
    )

    id = forms.URLField(
        initial="",
        label=_("Id"),
        required=False
    )

    trust_mark = forms.CharField(
        initial = "",
        label=_("Enter trust mark"),
        required=False
    )


class OnboardingDecodeForm(forms.Form):

    jwt = forms.CharField(
        initial="",
        label=_("jwt"),
        error_messages={"required": _("Enter a jwt")},
    )

    jwk = forms.JSONField(
        initial=dict,
        label=_("jwk"),
        required=False,
    )
