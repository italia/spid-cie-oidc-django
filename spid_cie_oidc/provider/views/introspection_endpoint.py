import logging

from djagger.decorators import schema
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.views import View
from spid_cie_oidc.onboarding.schemas.introspection_request import IntrospectionRequest
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionErrorResponseSpid, IntrospectionResponse
from spid_cie_oidc.provider.exceptions import ValidationException
from spid_cie_oidc.provider.models import IssuedToken

from . import OpBase
logger = logging.getLogger(__name__)


@schema(
    methods=['GET', 'POST'],
    dj_post_request_schema=IntrospectionRequest,
    dj_post_response_schema= {
            "200":IntrospectionResponse,
            "400": IntrospectionErrorResponseSpid
    },
    dj_get_response_schema= {
            "400": {}
    },
)
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
