import logging
from django.conf import settings
from pydantic import ValidationError

from django.urls import reverse
from django.http import HttpResponseRedirect
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from ..oidc import *
from ..oauth2 import *

from enum import Enum

from spid_cie_oidc.entity.exceptions import InvalidTrustchain
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.utils import get_key
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.relying_party.exceptions import ValidationException
from spid_cie_oidc.relying_party.settings import (
    RP_DEFAULT_PROVIDER_PROFILES,
    RP_PROVIDER_PROFILES
)

logger = logging.getLogger(__name__)


class TokenRequestType(str, Enum):
    refresh = "refresh"
    revocation = "revocation"
    introspection = "introspection"


class SpidCieOidcRp:
    """
    Baseclass with common methods for RPs
    """

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

        trust_anchor = request.GET.get("trust_anchor", None)
        if trust_anchor is not None and trust_anchor not in settings.OIDCFED_TRUST_ANCHORS:
            logger.warning("Unallowed Trust Anchor")
            raise InvalidTrustchain("Unallowed Trust Anchor")

        if not trust_anchor:
            for profile, value in settings.OIDCFED_IDENTITY_PROVIDERS.items():
                if request.GET["provider"] in value:
                    trust_anchor = value[request.GET["provider"]]

        if not trust_anchor:
            trust_anchor = settings.OIDCFED_DEFAULT_TRUST_ANCHOR

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

    def get_token_request(self, auth_token, request, token_type):

        default_logout_url = getattr(
            settings, "LOGOUT_REDIRECT_URL", None
        ) or reverse("spid_cie_rp_landing")

        global audience
        authz = auth_token.authz_request

        rp_conf = FederationEntityConfiguration.objects.filter(
            sub=authz.client_id,
            is_active=True,
        ).first()

        token_request_data = dict(
            client_id=auth_token.authz_request.client_id,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        )

        if token_type == TokenRequestType.refresh:
            token_request_data["grant_type"] = "refresh_token"
            token_request_data["refresh_token"] = auth_token.refresh_token
            audience = authz.provider_configuration["token_endpoint"]

        elif token_type == TokenRequestType.revocation:
            token_request_data["token"] = auth_token.access_token
            audience = authz.provider_configuration["revocation_endpoint"]

        elif token_type == TokenRequestType.introspection:
            token_request_data["token"] = auth_token.access_token
            audience = authz.provider_configuration["introspection_endpoint"]

        if not audience:
            logger.warning(
                f"{authz.provider_id} doesn't expose the token ", token_type, " endpoint."
            )
            return HttpResponseRedirect(default_logout_url)
        # private_key_jwt
        client_assertion = create_jws(
            {
                "iss": authz.client_id,
                "sub": authz.client_id,
                "aud": [audience],
                "iat": iat_now(),
                "exp": exp_from_now(),
                "jti": str(uuid.uuid4())
            },
            jwk_dict = get_key(rp_conf.jwks_core)
        )
        token_request_data["client_assertion"] = client_assertion

        try:
            token_request = requests.post(
                audience,
                data=token_request_data,
                timeout=getattr(
                    settings, "HTTPC_TIMEOUT", 8
                )
            )  # nosec - B113

            if token_request.status_code != 200:  # pragma: no cover
                logger.error(
                    f"Something went wrong with refresh token request: {token_request.status_code}"
                )

            return token_request

        except Exception as e:  # pragma: no cover
            logger.error(f"Error in token request: {e}")
