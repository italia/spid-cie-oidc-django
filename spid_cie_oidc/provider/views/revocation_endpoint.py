import logging

from django.http import (
    HttpResponse,
    JsonResponse
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from spid_cie_oidc.provider.exceptions import ValidationException
from spid_cie_oidc.provider.models import IssuedToken

from . import OpBase
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class RevocationEndpoint(OpBase,View):

    def post(self, request, *args, **kwargs):
        try:
            self.validate_json_schema(
                request.POST.dict(),
                "revocation_request",
                "Revocation request object validation failed "
            )
            self.check_client_assertion(
                request.POST['client_id'],
                request.POST['client_assertion']
            )
        except ValidationException:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Revocation request object validation failed",
                },
                status = 400
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
            access_token = access_token,
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
