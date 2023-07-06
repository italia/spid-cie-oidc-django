import logging

from djagger.decorators import schema
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import OidcAuthenticationToken
from ..oauth2 import *
from ..oidc import *

from . import SpidCieOidcRp
from django.views import View

from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_payload,
)

logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Relying party refresh token request",
    methods=['GET'],
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Relying Party']
)
class SpidCieOidcRefreshToken(SpidCieOidcRp, View):
    error_template = "rp_error.html"
    def get(self, request, *args, **kwargs):
        """
            Call the token endpoint of the op
        """
        auth_tokens = OidcAuthenticationToken.objects.filter(
            user=request.user
        ).filter(revoked__isnull=True)

        default_logout_url = getattr(
            settings, "LOGOUT_REDIRECT_URL", None
        ) or reverse("spid_cie_rp_landing")
        if not auth_tokens:
            logger.warning(
                "Token request failed: not found any authentication session"
            )
            return HttpResponseRedirect(default_logout_url)

        auth_token = auth_tokens.last()

        authz = auth_token.authz_request

        rp_conf = FederationEntityConfiguration.objects.filter(
            sub=authz.client_id,
            is_active=True,
        ).first()

        # private_key_jwt
        client_assertion = create_jws(
            {
                "iss": authz.client_id,
                "sub": authz.client_id,
                "aud": [authz.provider_configuration["token_endpoint"]],
                "iat": iat_now(),
                "exp": exp_from_now(),
                "jti": str(uuid.uuid4()),
            },
            jwk_dict=rp_conf.jwks_core[0],
        )

        refresh_token_grant = dict(
            grant_type="refresh_token",
            refresh_token=auth_token.refresh_token,
            client_id=authz.client_id,
            client_assertion=client_assertion,
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        )
        try:
            refresh_token_request = requests.post(
                authz.provider_configuration["token_endpoint"],
                data=refresh_token_grant,
                timeout=getattr(
                    settings, "HTTPC_TIMEOUT", 8
                )
            )  # nosec - B113

            if refresh_token_request.status_code != 200:  # pragma: no cover
                logger.error(
                    f"Something went wrong with refresh token request: {refresh_token_request.status_code}"
                )
            else:
                try:
                    refresh_token_response = json.loads(refresh_token_request.content.decode())
                    auth_token.refresh_token=refresh_token_response["refresh_token"]
                    auth_token.access_token=refresh_token_response["access_token"]
                    auth_token.save()

                    logger.info(refresh_token_response)

                    decoded_access_token = unpad_jwt_payload(refresh_token_response["access_token"])
                    decoded_refresh_token = unpad_jwt_payload(refresh_token_response["refresh_token"])

                    request.session["rt_expiration"] = decoded_refresh_token['exp'] - iat_now()
                    request.session["rt_jti"] = decoded_refresh_token['jti']
                    request.session["oidc_rp_user_attrs"] = request.user.attributes

                    request.session["at_expiration"] = decoded_access_token['exp'] - iat_now()
                    request.session["at_jti"] = decoded_access_token['jti']

                    return HttpResponseRedirect(
                        getattr(
                            settings, "LOGIN_REDIRECT_URL", None
                        ) or reverse("spid_cie_rp_echo_attributes")
                    )

                except Exception as e:  # pragma: no cover
                    logger.error(f"Something went wrong: {e}")
        except Exception as e:  # pragma: no cover
            logger.warning(f"Refresh Token request failed: {e}")
