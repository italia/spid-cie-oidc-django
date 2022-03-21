import logging
from django.conf import settings
from pydantic import ValidationError
from spid_cie_oidc.entity.exceptions import InvalidTrustchain
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.statements import get_http_url
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.relying_party.exceptions import ValidationException
from spid_cie_oidc.relying_party.settings import (
    RP_DEFAULT_PROVIDER_PROFILES,
    RP_PROVIDER_PROFILES
)

logger = logging.getLogger(__name__)


class SpidCieOidcRp:
    """
    Baseclass with common methods for RPs
    """

    def get_jwks_from_jwks_uri(self, jwks_uri: str) -> dict:
        """
        get jwks
        """
        try:
            jwks_dict = get_http_url([jwks_uri], httpc_params=HTTPC_PARAMS).json()
        except Exception as e:
            logger.error(f"Failed to download jwks from {jwks_uri}: {e}")
            return {}
        return jwks_dict

    def get_oidc_op(self, request) -> TrustChain:
        """
            get available trust to a specific OP
        """
        if not request.GET.get("provider", None):
            logger.warning(
                "Missing provider url. Please try '?provider=https://provider-subject/'"
            )
            raise InvalidTrustchain(
                "Missing provider url. Please try '?provider=https://provider-subject/'"
            )
        trust_anchor = request.GET.get(
            "trust_anchor",
            settings.OIDCFED_IDENTITY_PROVIDERS.get(
                request.GET["provider"],
                settings.OIDCFED_DEFAULT_TRUST_ANCHOR
            )
        )

        if trust_anchor not in settings.OIDCFED_TRUST_ANCHORS:
            logger.warning("Unallowed Trust Anchor")
            raise InvalidTrustchain("Unallowed Trust Anchor")

        tc = TrustChain.objects.filter(
            sub=request.GET["provider"],
            trust_anchor__sub=trust_anchor,
        ).first()

        discover_trust = False
        if not tc:
            logger.info(f'Trust Chain not found for {request.GET["provider"]}')
            discover_trust = True

        elif not tc.is_active:
            logger.warning(f"{tc} found but DISABLED at {tc.modified}")
            raise InvalidTrustchain(f"{tc} found but DISABLED at {tc.modified}")

        elif tc.is_expired:
            logger.warning(f"{tc} found but expired at {tc.exp}")
            logger.warning("Try to renew the trust chain")
            discover_trust = True

        if discover_trust:
            tc = get_or_create_trust_chain(
                subject=request.GET["provider"],
                trust_anchor=trust_anchor,
                # TODO - not sure that it's required for a RP that fetches OP directly from TA
                # required_trust_marks = [],
                force=True,
            )
        return tc

    def validate_json_schema(self, request, schema_type, error_description):
        try:
            schema = RP_PROVIDER_PROFILES[RP_DEFAULT_PROVIDER_PROFILES]
            schema[schema_type](**request)
        except ValidationError as e:
            logger.error(
                f"{error_description} "
                f"for {request.get('client_id', None)}: {e}"
            )
            raise ValidationException()
