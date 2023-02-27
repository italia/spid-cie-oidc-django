import logging

from djagger.decorators import schema
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel
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
    methods=['GET', 'POST'],
    post_request_schema = {
        "application/x-www-form-urlencoded": schema_profile["introspection_request"]
    },
    post_response_schema= {
            "200":schema_profile["introspection_response"],
            "400":schema_profile["introspection_error_response"],
    },
    get_response_schema= {
            "400": BaseModel
    },
    tags = ['Provider']
)
@method_decorator(csrf_exempt, name="dispatch")
class IntrospectionEndpoint(OpBase, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def post(self, request, *args, **kwargs):
        try:
            self.validate_json_schema(
                request.POST.dict(),
                "introspection_request",
                "Introspection request object validation failed"
            )
            client_id = request.POST['client_id']
            self.check_client_assertion(
                client_id,
                request.POST['client_assertion']
            )
        except ValidationException:
            return JsonResponse(
                {
                    "error": "invalid_request",
                    "error_description": "Introspection request object validation failed",
                },
                status = 400
            )
        except Exception as e: # pragma: no cover
            logger.error(e)
            return HttpResponseForbidden()

        required_token = request.POST['token']
        # query con client_id, access token
        token = IssuedToken.objects.filter(
            access_token=required_token
        ).first()
        session = token.session
        if session.client_id != client_id:
            return JsonResponse( # pragma: no cover
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
