from spid_cie_oidc.entity.statements import (
    get_entity_configurations,
    EntityConfiguration,
)


def validate_entity_configuration(value):
    """
    value is the sub url
    """
    try:
        jwt = get_entity_configurations(value)[0]
    except Exception as e:
        raise ValidationError(
            f"Failed to fetch Entity Configuration for {value}: {e}"
        )
    ec = EntityConfiguration(jwt, httpc_params=HTTPC_PARAMS)
    ec.validate_by_itself()

    authority_hints = ec.payload.get("authority_hints", [])
    if not authority_hints:
        raise MissingAuthorityHintsClaim(
            "authority_hints must be present "
            "in a descendant entity configuration"
        )

    proper_descendant = False
    for i in authority_hints:
        if i in settings.OIDCFED_FEDERATION_TRUST_ANCHORS:
            proper_descendant = True
            break
    if not proper_descendant:
        raise NotDescendant(
            "This participant MUST have one of "
            f"{', '.join(settings.OIDCFED_FEDERATION_TRUST_ANCHORS)} in "
            f"its authority_hints claim. It has: {authority_hints}"
        )
