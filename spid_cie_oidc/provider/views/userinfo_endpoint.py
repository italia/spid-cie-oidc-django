import logging

from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from djagger.decorators import schema
from django.utils import timezone
from django.views import View
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    create_jwe,
    unpad_jwt_payload
)
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.entity.utils import get_jwks
from spid_cie_oidc.provider.models import IssuedToken

from . import OpBase
logger = logging.getLogger(__name__)


@schema(
    summary="OIDC Provider UserInfo endpoint",
    methods=['GET'],
    # TODO
    # security=[
    #     dict(
    #         description = "",
    #         name = "",
    #         bearerFormat = "JWT",
    #     )
    # ],
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Provider']
)
class UserInfoEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):
        """
            Userinfo endpoint just needs a HTTP GET with the Access Token
            in a Authorization Http Header like this:

            Authorization: Bearer $JWT
        """
        ah = request.headers.get("Authorization", None)
        if not ah or "Bearer " not in ah:
            return HttpResponseForbidden()
        bearer = ah.split("Bearer ")[1]

        token = IssuedToken.objects.filter(
            access_token=bearer,
            revoked=False,
            session__revoked=False,
            expires__gte=timezone.localtime(),
        ).first()

        if not token:
            return HttpResponseForbidden()

        rp_tc = TrustChain.objects.filter(
            sub=token.session.client_id,
            metadata__openid_relying_party__isnull=False,
            is_active=True
        ).first()
        if not rp_tc:
            return HttpResponseForbidden()

        issuer = self.get_issuer()
        access_token_data = unpad_jwt_payload(token.access_token)

        # TODO: user claims
        jwt = {"sub": access_token_data["sub"]}
        for claim in (
            token.session.authz_request.get(
                "claims", {}
            ).get("userinfo", {}).keys()
        ):
            if claim in token.session.user.attributes:
                jwt[claim] = token.session.user.attributes[claim]

        # sign the data
        jws = create_jws(jwt, issuer.jwks_core[0])

        # encrypt the data
        jwe = create_jwe(
            jws,
            get_jwks(
                rp_tc.metadata['openid_relying_party'],
                federation_jwks = rp_tc.jwks
            )[0],
            cty="JWT"
        )
        return HttpResponse(jwe, content_type="application/jose")
