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
    FederationHistoricalKey,
    TrustChain,
    StaffToken
)
from .settings import HTTPC_PARAMS
from .statements import OIDCFED_FEDERATION_WELLKNOWN_URL
from .utils import iat_now

logger = logging.getLogger(__name__)


def get_subs_from_wellknown(request, wkuri :str):
    sub = request.build_absolute_uri().split(wkuri)[0]

    sub_values = []
    if sub[-1] == "/":
        sub_values.extend((sub, sub[:-1]))
    elif sub[-1] != "/":
        sub_values.extend((sub, sub + "/"))
    return sub_values


def entity_configuration(request):
    """
    OIDC Federation Entity Configuration at
    .well-known/openid-federation
    """

    _sub_values = get_subs_from_wellknown(request, OIDCFED_FEDERATION_WELLKNOWN_URL)

    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub__in=_sub_values,
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


def openid_jwks(request, metadata_type:str, resource_type:str):
    """
        resource_tytpe = set(jwks_uri, jwks.jose)
    """
    _sub = request.build_absolute_uri().rsplit(resource_type)[0]
    _lookup = _sub.replace(f"/{metadata_type}/", "")
    conf = FederationEntityConfiguration.objects.filter(
        # TODO: check for reverse proxy and forwarders ...
        sub=_lookup,
        is_active=True,
    ).first()
    if not conf: # pragma: no cover
        raise Http404()
    content = conf.entity_configuration_as_dict['metadata'].get(
            metadata_type, {}
    ).get("jwks", {})

    if not content:
        raise Http404()

    if resource_type == 'jwks.json':
        return JsonResponse(content, safe=False)
    elif resource_type == 'jwks.jose':
        return HttpResponse(
            create_jws(content, conf.jwks_fed[0]),
            content_type="application/jose"
        )
    else:
        raise Http404()


def openid_connect_jwks_uri(request, metadata_type, resource_type="jwks.json"):
    """
    OpenID Connect default jwks_uri
    """
    return openid_jwks(request, metadata_type, resource_type)


def openid_connect_signed_jwks_uri(request, metadata_type, resource_type="jwks.jose"):
    """
    OpenID Federation signed_jwks_uri
    """
    return openid_jwks(request, metadata_type, resource_type)


def historical_keys(request):
    """
    OIDC Federation Entity Configuration at
    .well-known/openid-federation
    """

    sub_values = get_subs_from_wellknown(request, '.well-known/openid-federation-historical-jwks')
    keys = FederationHistoricalKey.objects.filter(entity__sub__in=sub_values)

    entity = keys.first().entity if keys.first() else None

    reg = {
        "iss": entity.sub if entity else sub_values[0],
        "iat": iat_now(),
        "keys": []
    }

    for i in keys:
        reg["keys"].append(i.as_dict)

    if request.GET.get("format") == "json": # pragma: no cover
        return JsonResponse(reg, safe=False)
    else:
        res = create_jws(
            reg,
            entity.jwks_fed[0],
            typ="jwk-set+jwt",
            # **kwargs,
        )

        return HttpResponse(
            res, content_type="application/jwk-set+jwt"
        )
