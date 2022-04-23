import logging

import requests

from djagger.decorators import schema
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from ..models import OidcAuthenticationToken
from ..oauth2 import *
from ..oidc import *

logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Relying party logout",
    methods=['GET'],
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Relying Party']
)
@login_required
def oidc_rpinitiated_logout(request):
    """
        Call the token revocation endpoint of the op
    """
    auth_tokens = OidcAuthenticationToken.objects.filter(
        user=request.user
    ).filter(revoked__isnull=True)

    default_logout_url = getattr(
        settings, "LOGOUT_REDIRECT_URL", None
    ) or reverse("spid_cie_rp_landing")
    if not auth_tokens:
        logger.warning(
            "Token revocation failed: not found any authentication session"
        )
        return HttpResponseRedirect(default_logout_url)

    auth_token = auth_tokens.last()
    authz = auth_token.authz_request
    provider_conf = authz.provider_configuration
    revocation_endpoint_url = provider_conf.get("revocation_endpoint")

    # first of all on RP side ...
    logger.info(f"{request.user} logout")
    logout(request)
    if not revocation_endpoint_url:
        logger.warning(
            f"{authz.provider_id} doesn't expose the token revocation endpoint."
        )
        return HttpResponseRedirect(default_logout_url)
    else:
        rp_conf = FederationEntityConfiguration.objects.filter(
            sub= authz.client_id,
            is_active=True,
        ).first()

        # private_key_jwt
        client_assertion = create_jws(
            {
                "iss": authz.client_id,
                "sub": authz.client_id,
                "aud": [revocation_endpoint_url],
                "iat": iat_now(),
                "exp": exp_from_now(),
                "jti": str(uuid.uuid4()),
            },
            jwk_dict=rp_conf.jwks_core[0],
        )

        auth_token.logged_out = timezone.localtime()
        auth_token.save()

        revocation_request = dict(
            token = auth_token.access_token,
            client_id = authz.client_id,
            client_assertion = client_assertion,
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        )
        try:
            requests.post(revocation_endpoint_url, data = revocation_request)
        except Exception as e: # pragma: no cover
            logger.warning(f"Token revocation failed: {e}")
        auth_tokens.update(revoked = timezone.localtime())
        return HttpResponseRedirect(default_logout_url)
