import base64
import hashlib
import logging
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.forms.utils import ErrorList
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse
)
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError as pydantic_ValidationError
from spid_cie_oidc.entity.exceptions import InvalidEntityConfiguration
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    encrypt_dict,
    unpad_jwt_payload
)
from spid_cie_oidc.entity.models import (
    TrustChain
)
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.provider.models import IssuedToken, OidcSession

from spid_cie_oidc.provider.exceptions import AuthzRequestReplay
from spid_cie_oidc.provider.forms import *
from spid_cie_oidc.provider.settings import *

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


@method_decorator(csrf_exempt, name="dispatch")
class RevocationEndpoint(OpBase,View):

    def post(self, request, *args, **kwargs):
        result = self.validate_json_schema(
            request.POST.dict(),
            "revocation_request",
            "Revocation request object validation failed "
        )
        if result:
            return result
        try:
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except Exception:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Validation of client assertion failed",

                },
                status = 400
            )

        access_token = request.POST.get('token', None)
        if not access_token:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "The request does not include Access Token",

                },
                status = 400
            )

        token = IssuedToken.objects.filter(
            access_token= access_token,
            revoked = False
        ).first()

        if not token or token.expired:
            return JsonResponse(
                {
                    "error": "invalid_grant",
                    "error_description": "Access Token not found or expired",

                },
                status = 400
            )

        if token.is_revoked:
            return JsonResponse(
                {
                    "error": "invalid_grant",
                    "error_description": "Access Token revoked",
                },
                status = 400
            )

        token.session.revoke()
        return HttpResponse()


class IntrospectionEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def post(self, request, *args, **kwargs):
        result = self.validate_json_schema(
            request.POST.dict(),
            "introspection_request",
            "Introspection request object validation failed"
        )
        if result:
            return result
        client_id = request.POST['client_id']
        try:
            self.check_client_assertion(
                client_id,
                request.POST['client_assertion']
            )
        except Exception:
            return HttpResponseForbidden()
        required_token = request.POST['token']
        # query con client_id, access token
        token = IssuedToken.objects.filter(
            access_token=required_token
        ).first()
        session = token.session
        if session.client_id != client_id:
            return JsonResponse(
                error = "invalid_client",
                error_description = "Client not recognized"
            )
        active = token and not token.is_revoked and not token.expired
        exp = token.expires
        sub = token.session.client_id
        issuer = self.get_issuer()
        iss = issuer.sub
        authz_request = session.authz_request
        scope = authz_request["scope"]
        response = {
            "active": active,
            "exp": exp,
            "sub" : sub,
            "iss": iss,
            "client_id": client_id,
            "aud": [client_id],
            "scope": scope
        }
        return JsonResponse(response)


def oidc_provider_not_consent(request):
    logout(request)
    urlrp = reverse("spid_cie_rp_callback")
    kwargs = dict(
        error = "invalid_request",
        error_description = _(
            "Authentication request rejected by user"
        )
    )
    url = f'{urlrp}?{urllib.parse.urlencode(kwargs)}'
    return HttpResponseRedirect(url)
