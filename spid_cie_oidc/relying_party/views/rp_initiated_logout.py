import logging


from djagger.decorators import schema
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from ..models import OidcAuthenticationToken

from . import SpidCieOidcRp, TokenRequestType
from django.views import View

logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Relying party logout",
    methods=['GET'],
    external_docs={
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags=['Relying Party']
)
class SpidCieOidcRpLogout(SpidCieOidcRp, View):
    def get(self, request):
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
        logger.info(f"{request.user} logout")
        logout(request)

        try:
            self.get_token_request(auth_token, request, TokenRequestType.revocation)  # "revocation")
            auth_token.logged_out = timezone.localtime()
            auth_token.save()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Token revocation failed: {e}")

        auth_tokens.update(revoked=timezone.localtime())
        return HttpResponseRedirect(default_logout_url)
