import logging

from djagger.decorators import schema
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import OidcAuthenticationToken
from ..oauth2 import *
from ..oidc import *

from . import SpidCieOidcRp, TokenRequestType
from django.views import View

from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_payload,
)

logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Relying party refresh token request",
    methods=['GET'],
    external_docs={
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags=['Relying Party']
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

        if not auth_tokens:
            logger.warning(
                "Token request failed: not found any authentication session"
            )

        auth_token = auth_tokens.last()

        try:
            token_response = self.get_token_request(auth_token, request, TokenRequestType.refresh)  # "refresh")
            if token_response.status_code == 400:
                return HttpResponseRedirect(reverse("spid_cie_rp_landing"))

            refresh_token_response = json.loads(token_response.content.decode())

            auth_token.refresh_token = refresh_token_response["refresh_token"]
            auth_token.access_token = refresh_token_response["access_token"]
            auth_token.save()

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
            logger.warning(f"Refresh Token request failed: {e}")
