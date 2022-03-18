
import base64
import hashlib
import logging

from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload
from spid_cie_oidc.provider.exceptions import ValidationException
from spid_cie_oidc.provider.models import IssuedToken, OidcSession

from . import OpBase
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TokenEndpoint(OpBase, View):

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def grant_auth_code(self, request, *args, **kwargs):
        """
            Token request for an authorization code grant
        """
        # PKCE check - based on authz.authz_request["code_challenge_method"] == S256
        code_challenge = hashlib.sha256(request.POST["code_verifier"].encode()).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        if code_challenge != self.authz.authz_request["code_challenge"]:
            return HttpResponseForbidden()
        #

        issued_token = IssuedToken.objects.filter(
            session= self.authz,
            revoked = False
        ).first()

        jwk_at = unpad_jwt_payload(issued_token.access_token)
        expires_in = self.get_expires_in(jwk_at['iat'], jwk_at['exp'])

        iss_token_data = dict( # nosec B106
            access_token = issued_token.access_token,
            id_token = issued_token.id_token,
            token_type = "Bearer", # nosec B106
            expires_in = expires_in,
            # TODO: remove unsupported scope
            scope = self.authz.authz_request["scope"],
        )
        if issued_token.refresh_token:
            iss_token_data['refresh_token'] = issued_token.refresh_token

        return JsonResponse(iss_token_data)

    def is_token_renewable(self, session) -> bool:
        issuedToken = IssuedToken.objects.filter(
            session = session
        )
        # TODO: check also ACR
        return (
            (issuedToken.count() - 1) < getattr(
                settings, "OIDCFED_PROVIDER_MAX_REFRESH", 1
            )
        )

    def grant_refresh_token(self, request, *args, **kwargs):
        """
            client_id=https://rp.cie.it&
            client_assertion=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlNQSUQiLCJhZG1pbiI6dHJ1ZX0.LVyRDPVJm0S9q7oiXcYVIIqGWY0wWQlqxvFGYswL...&
            client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&
            refresh_token=8xLOxBtZp8 &
            grant_type=refresh_token
        """
        # 1. get the IssuedToken refresh one, revoked = None
        # 2. create a new instance of issuedtoken linked to the same sessions and revoke the older
        # 3. response with a new refresh, access and id_token
        issued_token = IssuedToken.objects.filter(
            refresh_token = request.POST['refresh_token'],
            revoked = False
        ).first()

        if not issued_token:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Refresh token not found",

                },
                status = 400
            )

        session = issued_token.session
        if not self.is_token_renewable(session):
            return JsonResponse(
                    {
                        "error": "invalid_request",
                        "error_description": "Refresh Token can no longer be updated",

                    }, status = 400
            )
        iss_token_data = self.get_iss_token_data(session, self.get_issuer())
        IssuedToken.objects.create(**iss_token_data)
        issued_token.revoked = True
        issued_token.save()

        jwk_at = unpad_jwt_payload(iss_token_data['access_token'])
        expires_in = self.get_expires_in(jwk_at['iat'], jwk_at['exp'])

        data = dict( # nosec B106
            access_token = iss_token_data['access_token'],
            id_token = iss_token_data['id_token'],
            token_type = "Bearer", # nosec B106
            expires_in = expires_in,
            # TODO: remove unsupported scope
            scope = self.authz.authz_request["scope"],
        )
        if issued_token.refresh_token:
            data['refresh_token'] = issued_token.refresh_token

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        logger.debug(f"{request.headers}: {request.POST}")
        try:
            self.validate_json_schema(
                request.POST.dict(),
                request.POST["grant_type"],
                "Token request object validation failed "
            )
        except ValidationException:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Token request object validation failed",
                },
                status = 400
            )

        self.commons = self.get_jwt_common_data()
        self.issuer = self.get_issuer()

        self.authz = OidcSession.objects.filter(
            auth_code=request.POST["code"],
            revoked=False
        ).first()

        if not self.authz:
            return HttpResponseBadRequest()

        # check client_assertion and client ownership
        try:
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except Exception:
            # TODO: coverage test
            return JsonResponse(
                # TODO: error message here
                {
                    'error': "unauthorized_client",
                    'error_description': ""

                }, status = 403
            )
        if request.POST.get("grant_type") == 'authorization_code':
            return self.grant_auth_code(request)
        elif request.POST.get("grant_type") == 'refresh_token':
            return self.grant_refresh_token(request)
        else:
            # Token exchange? :-)
            raise NotImplementedError()
