import json
import logging
import uuid
from copy import deepcopy

from djagger.decorators import schema
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views import View
from spid_cie_oidc.entity.exceptions import InvalidTrustchain
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.utils import get_jwks
from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.relying_party.settings import OIDCFED_ACR_PROFILES, RP_PROVIDER_PROFILES, RP_DEFAULT_PROVIDER_PROFILES

from ..models import OidcAuthentication
from ..settings import (
    RP_PKCE_CONF,
    RP_REQUEST_CLAIM_BY_PROFILE,
    RP_REQUEST_EXP
)
from ..utils import (
    http_dict_to_redirect_uri_path,
    random_string,
)

from . import SpidCieOidcRp

logger = logging.getLogger(__name__)

schema_profile = RP_PROVIDER_PROFILES[RP_DEFAULT_PROVIDER_PROFILES]


@schema(
    summary="OIDC Relying Party Authorization begin",
    methods=['GET'],
    get_response_schema= {
        "302": schema_profile["authorization_request_doc"],
    },
    external_docs = {
        "alt_text": "AgID SPID OIDC Guidelines",
        "url": "https://www.agid.gov.it/it/agenzia/stampa-e-comunicazione/notizie/2021/12/06/openid-connect-spid-adottate-linee-guida"
    },
    tags = ['Relying Party']
)
class SpidCieOidcRpBeginView(SpidCieOidcRp, View):
    """
        View which processes the actual Authz request and
        returns a Http Redirect
    """
    error_template = "rp_error.html"

    def get(self, request, *args, **kwargs):
        """
        http://localhost:8001/oidc/rp/authorization?provider=http://127.0.0.1:8002/&profile=spid
        """
        try:
            tc = self.get_oidc_op(request)
            if not tc:
                context = {
                    "error": "request rejected",
                    "error_description": "Trust Chain is unavailable.",
                }
                return render(request, self.error_template, context)

        except InvalidTrustchain as exc:
            context = {
                "error": "request rejected",
                "error_description": str(exc.args),
            }
            return render(request, self.error_template, context, status=404)

        except Exception as exc:
            context = {
                "error": "request rejected",
                "error_description": _(str(exc.args)),
            }
            return render(request, self.error_template, context)

        provider_metadata = tc.metadata.get('openid_provider', None)
        if not provider_metadata:
            context = {
                "error": "request rejected",
                "error_description": _("provider metadata not found"),
            }
            return render(request, self.error_template, context, status=404)

        entity_conf = FederationEntityConfiguration.objects.filter(
            entity_type="openid_relying_party",
            # TODO: RPs multitenancy?
            # sub = request.build_absolute_uri()
        ).first()
        if not entity_conf:
            context = {
                "error": "request rejected",
                "error_description": _("Missing configuration."),
            }
            return render(request, self.error_template, context, status=404)

        client_conf = entity_conf.metadata["openid_relying_party"]
        if not (
            # TODO
            # provider_metadata.get("jwks_uri", None)
            # or
            provider_metadata.get("jwks", None)
        ):
            context = {
                "error": "request rejected",
                "error_description": _("Invalid provider Metadata."),
            }
            return render(request, self.error_template, context, status=404)

        jwks_dict = get_jwks(provider_metadata, federation_jwks=tc.jwks)

        # stores the resolves jwks in the provider metadata linked to this authz request
        provider_metadata['jwks'] = {'keys': jwks_dict}
        if not jwks_dict:
            _msg = f"Failed to get jwks from {tc.sub}"
            logger.error(_msg)
            context = {
                "error": "request rejected",
                "error_description": _msg
            }
            return render(request, self.error_template, context)

        authz_endpoint = provider_metadata["authorization_endpoint"]

        redirect_uri = request.GET.get("redirect_uri", client_conf["redirect_uris"][0])
        if redirect_uri not in client_conf["redirect_uris"]:
            logger.warning(
                f"Requested for unknown redirect uri {redirect_uri}. "
                f"Reverted to default {client_conf['redirect_uris'][0]}."
            )
            redirect_uri = client_conf["redirect_uris"][0]
        _profile = request.GET.get("profile", "spid")
        _timestamp_now = int(timezone.localtime().timestamp())
        authz_data = dict(
            iss=client_conf["client_id"],
            scope= request.GET.get("scope", None) or "openid",
            redirect_uri=redirect_uri,
            response_type=client_conf["response_types"][0],
            nonce=random_string(32),
            state=random_string(32),
            client_id=client_conf["client_id"],
            endpoint=authz_endpoint,
            acr_values= OIDCFED_ACR_PROFILES,
            iat=_timestamp_now,
            exp =_timestamp_now + RP_REQUEST_EXP,
            jti = str(uuid.uuid4()),
            aud=[tc.sub, authz_endpoint],
            claims=RP_REQUEST_CLAIM_BY_PROFILE[_profile],
        )

        _prompt = request.GET.get("prompt", "consent login")

        # if "offline_access" in authz_data["scope"]:
        # _prompt.extend(["consent login"])

        authz_data["prompt"] = _prompt

        # PKCE
        pkce_func = import_string(RP_PKCE_CONF["function"])
        pkce_values = pkce_func(**RP_PKCE_CONF["kwargs"])
        authz_data.update(pkce_values)
        #
        authz_entry = dict(
            client_id=client_conf["client_id"],
            state=authz_data["state"],
            endpoint=authz_endpoint,
            # TODO: better have here an organization name
            provider_id=tc.sub,
            data=json.dumps(authz_data),
            provider_configuration=provider_metadata,
        )

        # TODO: Prune the old or unbounded authz ...
        OidcAuthentication.objects.create(**authz_entry)

        authz_data.pop("code_verifier")
        # add the signed request object
        authz_data_obj = deepcopy(authz_data)
        authz_data_obj["iss"] = client_conf["client_id"]

        # sub claim MUST not be used to prevent that this jwt
        # could be reused as a private_key_jwt
        # authz_data_obj["sub"] = client_conf["client_id"]

        request_obj = create_jws(authz_data_obj, entity_conf.jwks_core[0])
        authz_data["request"] = request_obj
        uri_path = http_dict_to_redirect_uri_path(
            {
                "client_id": authz_data["client_id"],
                "scope" : authz_data["scope"],
                "response_type": authz_data["response_type"],
                "code_challenge": authz_data["code_challenge"],
                "code_challenge_method": authz_data["code_challenge_method"],
                "request": authz_data["request"]
            }
        )
        url = "?".join((authz_endpoint, uri_path))
        logger.info(f"Starting Authz request to {url}")
        return HttpResponseRedirect(url)
