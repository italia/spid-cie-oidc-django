import logging
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.utils import timezone
from django.views import View
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    encrypt_dict,
    unpad_jwt_payload
)
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.provider.models import IssuedToken


from . import OpBase
logger = logging.getLogger(__name__)


class UserInfoEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):

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
            type="openid_relying_party",
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
        jws = create_jws(jwt, issuer.jwks[0])

        # encrypt the data
        jwe = encrypt_dict(jws, rp_tc.metadata["jwks"]["keys"][0])
        return HttpResponse(jwe, content_type="application/jose")
