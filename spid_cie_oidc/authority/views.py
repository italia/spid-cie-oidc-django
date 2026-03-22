import logging
import math
import urllib.parse

from djagger.decorators import schema
from django.conf import settings
from django.core.paginator import Paginator
from django.http import (
    HttpResponse,
    JsonResponse,
)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from spid_cie_oidc.authority.models import (
    FederationDescendant,
    FederationEntityAssignedProfile
)
from spid_cie_oidc.authority.settings import MAX_ENTRIES_PAGE
from spid_cie_oidc.entity.jwtse import (
    create_jws,
    unpad_jwt_head,
    unpad_jwt_payload,
)
from spid_cie_oidc.entity.models import get_first_self_trust_anchor
from spid_cie_oidc.entity.statements import get_trust_mark_type_id
from spid_cie_oidc.entity.utils import iat_now

from . schemas.fetch_endpoint_request import FetchRequest, FedAPIErrorResponse, FetchResponse
from . schemas.list_endpoint import ListRequest, ListResponse
from . schemas.advanced_entity_list_endpoint import AdvancedEntityListRequest, AdvancedEntityListResponse
from . schemas.trust_mark_status_endpoint import (
    TrustMarkRequest,
    TrustMarkResponse,
)

logger = logging.getLogger(__name__)


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": FetchRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": FetchResponse
    },
    tags = ['Federation API']
)
def fetch(request):
    """
    OpenID Federation 8.1: Fetch endpoint.
    Request: GET with sub REQUIRED (issuer implied by this endpoint's URL).
    """
    iss = get_first_self_trust_anchor()

    if not request.GET.get("sub"):
        conf = get_first_self_trust_anchor()
        if request.GET.get("format") == "json":
            return JsonResponse(conf.entity_configuration_as_dict, safe=False)
        return HttpResponse(
            conf.entity_configuration_as_jws,
            content_type="application/entity-statement+jwt"
        )

    sub = FederationDescendant.objects.filter(
        sub=request.GET["sub"], is_active=True
    ).first()
    if not sub:
        return JsonResponse(
            {
                "error": "invalid_subject",
                "error_description": "entity not found"
            },
            status=404
        )

    if request.GET.get("format") == "json":
        return JsonResponse(
            sub.entity_statement_as_dict(iss.sub), safe=False
        )
    return HttpResponse(
        sub.entity_statement_as_jws(iss.sub),
        content_type="application/entity-statement+jwt",
    )


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": ListRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": ListResponse
    },
    tags = ['Federation API']
)
def entity_list(request):
    """
    OpenID Federation 8.2: Subordinate Listing.
    Optional filters: entity_type, trust_marked, trust_mark_type, intermediate.
    """
    _q = {"descendant__is_active": True}

    if request.GET.get("intermediate", "").lower() == "true":
        _q["profile__profile_category"] = "federation_entity"
    elif request.GET.get("entity_type"):
        _q["profile__profile_category"] = request.GET["entity_type"]

    if request.GET.get("trust_mark_type"):
        _q["profile__profile_id"] = request.GET["trust_mark_type"]

    entries = FederationEntityAssignedProfile.objects.filter(**_q).values_list(
        "descendant__sub", flat=True
    )
    return JsonResponse(list(set(entries)), safe=False)


# TODO - add the schema
# @schema(
    # methods=['GET'],
    # get_request_schema = {
    # "application/x-www-form-urlencoded": ListRequest
    # },
    # get_response_schema = {
    # "400": FedAPIErrorResponse,
    # "404": FedAPIErrorResponse,
    # "200": ListResponse
    # },
    # tags = ['Federation API']
# )
def trust_marked_list(request):
    if request.GET.get("trust_mark_id", "").lower():
        _q = {"profile__profile_id": request.GET["trust_mark_id"]}
    else:
        _q = {}

    entries = FederationEntityAssignedProfile.objects.filter(**_q).values_list(
        "descendant__sub", flat=True
    )
    return JsonResponse(list(set(entries)), safe=False)


@schema(
    methods=['GET'],
    get_request_schema = {
        "application/x-www-form-urlencoded": AdvancedEntityListRequest
    },
    get_response_schema = {
            "400": FedAPIErrorResponse,
            "404": FedAPIErrorResponse,
            "200": AdvancedEntityListResponse
    },
    tags = ['Federation API']
)
def advanced_entity_listing(request):
    desecendants = FederationDescendant.objects.filter(
        is_active = True,
    ).order_by("-modified")
    entities_list = []
    for descendant in desecendants:
        try:
            _ss = descendant.entity_statement_as_jws()
        except AttributeError as e:
            logger.warning(
                f"Subordinate {descendant} missing authority hint: {e}"
            )
            continue

        entity = {
            descendant.sub : {
                "iat" : int(descendant.modified.timestamp()),
                "subordinate_statement": _ss
            }
        }
        entities_list.append(entity)
    total_entries = desecendants.count()

    _max_entries = getattr(settings, 'MAX_ENTRIES_PAGE', MAX_ENTRIES_PAGE)
    p = Paginator(entities_list, _max_entries)
    page = request.GET.get("page", 1)
    entities = p.get_page(page)
    next_page_path = ""
    if entities.has_next():
        param = {"page": entities.next_page_number()}
        url = f'{reverse("oidcfed_advanced_entity_listing")}?{urllib.parse.urlencode(param)}'
        next_page_path = f"{url}"
    prev_page_path = ""
    if entities.has_previous():
        param = {"page": entities.previous_page_number()}
        url = f'{reverse("oidcfed_advanced_entity_listing")}?{urllib.parse.urlencode(param)}'
        prev_page_path = f"{url}"
    try:
        iss = get_first_self_trust_anchor().sub
    except Exception:
        return JsonResponse(
            {
                "error": "Missing trust anchor",
            },
            status = 404
        )
    res = {
            "iss" : iss,
            "iat" : iat_now(),
            "entities" : entities_list,
            "page" : int(page),
            "total_pages" : math.ceil(total_entries / MAX_ENTRIES_PAGE),
            "total_entries" : total_entries,
            "next_page_path": next_page_path,
            "prev_page_path": prev_page_path,
    }
    return JsonResponse(res, safe=False)


@schema(
    methods=['GET', 'POST'],
    get_request_schema={
        "application/x-www-form-urlencoded": TrustMarkRequest
    },
    get_response_schema={
        "400": FedAPIErrorResponse,
        "404": FedAPIErrorResponse,
        "200": TrustMarkResponse
    },
    tags=['Federation API']
)
@csrf_exempt
def trust_mark_status(request):
    """
    OpenID Federation 8.4: Trust Mark Status endpoint.
    Request: trust_mark (JWT) REQUIRED [draft 48], or legacy: sub + trust_mark_id/trust_mark_type/id.
    Response: 200 application/trust-mark-status-response+jwt (signed JWT), or 404 not_found.
    """
    sub = request.POST.get("sub") or request.GET.get("sub", None)
    _id = (
        request.POST.get("trust_mark_type") or request.GET.get("trust_mark_type")
        or request.POST.get("trust_mark_id") or request.GET.get("trust_mark_id")
        or request.POST.get("id") or request.GET.get("id")
    )
    trust_mark_jwt = request.POST.get("trust_mark") or request.GET.get("trust_mark", None)

    if request.method not in ("GET", "POST"):
        return JsonResponse(
            {"error": "invalid_request", "error_description": "Method not allowed"},
            status=400
        )

    if trust_mark_jwt:
        try:
            unpad_jwt_head(trust_mark_jwt)
            payload = unpad_jwt_payload(trust_mark_jwt)
            sub = payload.get("sub")
            _id = get_trust_mark_type_id(payload)
        except Exception:
            return JsonResponse(
                {"error": "invalid_request", "error_description": "Invalid trust_mark JWT"},
                status=400
            )
    elif not (sub and _id):
        return JsonResponse(
            {"error": "invalid_request", "error_description": "trust_mark REQUIRED or sub + trust_mark_type/id"},
            status=400
        )

    assigned = FederationEntityAssignedProfile.objects.filter(
        descendant__sub=sub,
        profile__profile_id=_id,
        descendant__is_active=True,
    ).select_related("issuer").first()

    if not assigned:
        return JsonResponse(
            {"error": "not_found", "error_description": "Trust Mark not found or not active"},
            status=404
        )

    # Draft 48: response is signed JWT with iss, iat, trust_mark, status
    tm_jwt_for_response = trust_mark_jwt or assigned.trust_mark.get("trust_mark") or assigned.trust_mark_as_jws
    issuer = assigned.issuer
    jwk = issuer.jwks_fed[0]
    status_payload = {
        "iss": issuer.sub,
        "iat": iat_now(),
        "trust_mark": tm_jwt_for_response,
        "status": "active",
    }
    signed = create_jws(
        status_payload,
        jwk,
        alg=issuer.default_signature_alg,
        protected={"typ": "trust-mark-status-response+jwt", "kid": jwk.get("kid")},
    )
    return HttpResponse(
        signed,
        content_type="application/trust-mark-status-response+jwt",
        status=200,
    )
