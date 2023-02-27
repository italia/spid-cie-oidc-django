import logging

from djagger.decorators import schema
from django.http import (
    HttpResponse,
    JsonResponse
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from spid_cie_oidc.provider.exceptions import ValidationException
from spid_cie_oidc.provider.models import IssuedToken
from spid_cie_oidc.provider.settings import (
    OIDCFED_DEFAULT_PROVIDER_PROFILE,
    OIDCFED_PROVIDER_PROFILES
)

from . import OpBase
logger = logging.getLogger(__name__)


schema_profile = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]


@schema(
    methods=['POST'],
    post_request_schema = {
        "application/x-www-form-urlencoded": schema_profile["revocation_request"],
        "application/json": schema_profile["revocation_request"],
    },
    post_response_schema = {
            "200": {},
            "400": schema_profile["revocation_response"]
    },
    tags = ['Provider']
)
@method_decorator(csrf_exempt, name="dispatch")
class RevocationEndpoint(OpBase, View):

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
        except ValidationException: # pragma: no cover
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
        if not access_token: # pragma: no cover
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

        if token.is_revoked: # pragma: no cover
            return JsonResponse(
                {
                    "error": "invalid_grant",
                    "error_description": "Access Token revoked",
                },
                status = 400
            )

        token.session.revoke()
        return HttpResponse()
