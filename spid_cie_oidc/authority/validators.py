import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string

from spid_cie_oidc.entity.statements import (
    OIDCFED_FEDERATION_WELLKNOWN_URL,
    get_entity_configurations,
    EntityConfiguration,
)

from spid_cie_oidc.entity import settings as entity_settings
from spid_cie_oidc.entity.exceptions import MissingAuthorityHintsClaim, NotDescendant

logger = logging.getLogger(__name__)
HTTPC_PARAMS = getattr(settings, "HTTPC_PARAMS", entity_settings.HTTPC_PARAMS)


def validate_entity_configuration(value):
    """
    value is the sub url
    """
    jwt = None
    try:
        jwt = get_entity_configurations(value)[0]
    except Exception as e:
        raise ValidationError(
            f"Failed to fetch Entity Configuration for {value}: {e}"
        )
    if not jwt: # pragma: no cover
        raise ValidationError(
            "failed to get a valid Entity Configuration from "
            f"{value}{OIDCFED_FEDERATION_WELLKNOWN_URL}"
        )

    try:
        ec = EntityConfiguration(jwt, httpc_params=HTTPC_PARAMS)
        ec.validate_by_itself()
    except Exception as e: # pragma: no cover
        raise ValidationError(
            f"Failed to fetch Entity Configuration for {value}: {e}"
        )

    authority_hints = ec.payload.get("authority_hints", [])
    if not authority_hints:
        raise MissingAuthorityHintsClaim(
            "authority_hints must be present in "
            "a descendant entity configuration"
        )

    superior_sub = import_string(
        "spid_cie_oidc.entity.models.get_first_self_trust_anchor"
    )().sub
    if superior_sub not in authority_hints:
        raise NotDescendant(
            f"This participant MUST have {superior_sub} in"
            f"its authority_hints claim. It has: {authority_hints}."
        )
    return ec
