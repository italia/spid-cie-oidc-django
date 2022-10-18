import logging

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib import messages

# from prettyjson import PrettyJSONWidget

from django.conf import settings
from .jwtse import unpad_jwt_payload
from .statements import EntityConfiguration, get_entity_configurations, get_entity_statements
from .models import (
    FederationEntityConfiguration,
    FetchedEntityStatement,
    TrustChain,
    StaffToken
)
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain

from . settings import HTTPC_PARAMS

logger = logging.getLogger(__name__)


@admin.register(FederationEntityConfiguration)
class FederationEntityConfigurationAdmin(admin.ModelAdmin):
    # formfield_overrides = {
    # JSONField: {
    # "widget": PrettyJSONWidget(
    # attrs={"initial": "parsed", "disabled": True}
    # )
    # }
    # }

    @admin.action(description='update trust marks')
    def update_trust_marks(modeladmin, request, queryset):  # pragma: no cover
        """
        fetch trust marks from all the authorities
        """
        trust_marks = {}

        for obj in queryset:
            jwts = get_entity_configurations(obj.authority_hints, HTTPC_PARAMS)
            for jwt in jwts:

                try:
                    ec = EntityConfiguration(jwt, httpc_params=HTTPC_PARAMS)
                except Exception as e:
                    _msg = f"Failed getting Entity Configuration for {jwt}: {e}"
                    logger.warning(_msg)
                    messages.error(_msg)
                    continue

                try:
                    # get superior fetch url
                    fetch_api_url = ec.payload["metadata"]["federation_entity"][
                        "federation_fetch_endpoint"
                    ]
                except KeyError:
                    _msg = (
                        "Missing federation_fetch_endpoint in  "
                        f"federation_entity metadata for {obj.sub} by {ec.sub}."
                    )
                    logger.warning(_msg)
                    messages.error(_msg)
                    continue

                _url = f"{fetch_api_url}?sub={obj.sub}"
                try:
                    logger.info(f"Getting entity statements from {_url}")
                    _jwts = get_entity_statements([_url], HTTPC_PARAMS)

                    payload = unpad_jwt_payload(_jwts[0])
                    for i in payload.get("trust_marks", []):
                        trust_marks[i['id']] = i['trust_mark']
                except Exception as e:
                    _msg = f"Error getting entity statements from {_url}: {e}"
                    logger.warning(_msg)
                    messages.error(_msg)
                    continue

            positions = {}
            count = 0
            for i in obj.trust_marks:
                positions[i['id']] = count
                count += 1

            if positions:
                for k,v in trust_marks.items():
                    if positions.get(k, None):
                        obj.trust_marks[positions[k]] = {k:v}
                    else:
                        obj.trust_marks.append({k:v})
            else:
                obj.trust_marks = [
                    {"id":k, "trust_mark":v} for k,v in trust_marks.items()
                ]

            obj.save()
            messages.success(
                request,
                f"Trust mark reloaded succesfully: {', '.join(trust_marks.keys())}"
            )

    list_display = (
        "sub",
        "type",
        "kids",
        "is_active",
        "created",
    )
    list_filter = ("created", "modified", "is_active")
    # search_fields = ('command__name',)
    readonly_fields = (
        "created",
        "modified",
        "entity_configuration_as_json",
        "pems_as_html",
        "kids",
        "type",
    )
    actions = [update_trust_marks]

    def pems_as_html(self, obj):
        res = ""
        data = dict()
        for k, v in obj.pems_as_dict.items():
            data[k] = {}
            for i in ("public", "private"):
                data[k][i] = v[i].replace("\n", "<br>")
            res += (
                f"<b>{k}</b><br><br>"
                f"{data[k]['public']}<br>"
                f"{data[k]['private']}<br><hr>"
            )
        return mark_safe(res)  # nosec


@admin.register(TrustChain)
class TrustChainAdmin(admin.ModelAdmin):

    @admin.action(description='reload trust chain')
    def update_trust_chain(modeladmin, request, queryset): # pragma: no cover
        for tc in queryset:
            sub = tc.sub
            ta = tc.trust_anchor.sub
            try :
                get_or_create_trust_chain(
                    subject=sub,
                    trust_anchor=ta,
                    httpc_params=settings.HTTPC_PARAMS,
                    required_trust_marks=getattr(
                        settings, "OIDCFED_REQUIRED_TRUST_MARKS", [],
                    ),
                    force=True
                )
                messages.success(
                    request, f"Trust chain successfully reloaded for {sub}"
                )
            except Exception as e:
                messages.error(request, f"Failed to update {sub} due to: {e}")
                continue

    list_display = ("sub", "exp", "modified", "is_valid")
    list_filter = ("exp", "modified", "is_active")
    search_fields = ("sub",)
    readonly_fields = (
        "created",
        "modified",
        "parties_involved",
        "metadata",
        "status",
        "log",
        "chain",
        "iat",
    )
    actions = [update_trust_chain]


@admin.register(FetchedEntityStatement)
class FetchedEntityStatementAdmin(admin.ModelAdmin):
    list_display = ("sub", "iss", "exp", "iat", "created", "modified")
    list_filter = ("created", "modified", "exp", "iat")
    search_fields = ("sub", "iss")
    readonly_fields = ("sub", "statement", "created", "modified", "iat", "exp", "iss")


@admin.register(StaffToken)
class StaffTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expire_at", "is_valid")
    list_filter = ("created", "modified", "expire_at")
    search_fields = ("token", )
    readonly_fields = ("is_valid",)
    raw_id_fields = ('user',)
