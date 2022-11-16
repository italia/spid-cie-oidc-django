import logging

from django.conf import settings
from djagger.decorators import schema
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse

from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.schemas.resolve_endpoint import (
    ResolveRequest, ResolveResponse, ResolveErrorResponse
)
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain

from .models import (
    FederationEntityConfiguration,
    TrustChain,
    StaffToken,
    get_first_self_trust_anchor
)
from .settings import HTTPC_PARAMS
from .statements import OIDCFED_FEDERATION_WELLKNOWN_URL


logger = logging.getLogger(__name__)


def entity_configuration(request):
    """
    OIDC Federation Entity Configuration at
    .well-known/openid-federation
    """
    _sub = request.build_absolute_uri().split(OIDCFED_FEDERATION_WELLKNOWN_URL)[0]
    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub=_sub,
        is_active=True,
    ).first()

    if not conf: # pragma: no cover
        raise Http404()

    if request.GET.get("format") == "json": # pragma: no cover
        return JsonResponse(conf.entity_configuration_as_dict, safe=False)
    else:
        return HttpResponse(
            conf.entity_configuration_as_jws, content_type="application/entity-statement+jwt"
        )


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": ResolveRequest
    },
    get_response_schema = {
            "400": ResolveErrorResponse,
            "404": ResolveErrorResponse,
            "200": ResolveResponse
    },
    tags = ['Federation API']
)
def resolve_entity_statement(request, format: str = "jose"):
    """
    resolves the final metadata of its descendants

    In this implementation we only returns a preexisting
    Metadata if it's valid
    we avoid any possibility to trigger a new Metadata discovery if
    """

    if not all((request.GET.get("sub", None), request.GET.get("anchor", None))):
        raise Http404("sub and anchor parameters are REQUIRED.")

    iss = FederationEntityConfiguration.objects.filter(is_active=True).first()

    _q = dict(
        sub=request.GET["sub"],
        trust_anchor__sub=request.GET["anchor"],
        is_active=True
    )

    # gets the cached one
    entity = TrustChain.objects.filter(**_q).first()

    # only with privileged actors with staff token can triggers a new trust chain
    staff_token_head = request.headers.get("Authorization", None)
    if staff_token_head:
        staff_token = StaffToken.objects.filter(
            token = staff_token_head
        ).first()
        if staff_token.is_valid:
            try:
                # a staff token get a fresh trust chain on each call
                entity = get_or_create_trust_chain(
                    httpc_params=HTTPC_PARAMS,
                    required_trust_marks = getattr(
                        settings, "OIDCFED_REQUIRED_TRUST_MARKS", []
                    ),
                    subject=_q["sub"],
                    trust_anchor=_q["trust_anchor__sub"],
                    force = True
                )
            except Exception as e:
                logger.error(
                    f"Failed privileged Trust Chain creation for {_q['sub']}: {e}"
                )

    if not entity:
        raise Http404("entity not found.")

    res = {
        "iss": iss.sub,
        "sub": request.GET["sub"],
        # "aud": [],
        "iat": entity.iat_as_timestamp,
        "exp": entity.exp_as_timestamp,
        "trust_marks": entity.trust_marks,
        "metadata": entity.metadata,
        "trust_chain": entity.chain
    }

    if request.GET.get("format") == "json" or format == "json":
        return JsonResponse(res, safe=False)
    else:
        return HttpResponse(
            create_jws(res, iss.jwks_fed[0]),
            content_type="application/jose",
        )
