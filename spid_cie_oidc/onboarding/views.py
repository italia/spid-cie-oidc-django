import json
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _

from spid_cie_oidc.authority.schemas.fetch_endpoint_request import FetchRequest
from spid_cie_oidc.authority.schemas.list_endpoint import ListRequest, ListResponse
from spid_cie_oidc.entity.schemas.resolve_endpoint import ResolveRequest, ResolveResponse
from spid_cie_oidc.authority.schemas.trust_mark_status_endpoint import TrustMarkRequest, TrustMarkResponse
from spid_cie_oidc.entity.schemas.fa_metadata import FAMetadata


from .forms import (
    OnboardingRegistrationForm,
    OnboardingCreateTrustChain,
    OnboardingValidatingTrustMarkForm,
    OnboardingDecodeForm
)
from .models import OnBoardingRegistration
from spid_cie_oidc.entity.jwks import (
    private_pem_from_jwk,
    public_pem_from_jwk,
    new_rsa_key,
    serialize_rsa_key,
    private_jwk_from_pem,
    public_jwk_from_pem
)

from spid_cie_oidc.entity.jwtse import unpad_jwt_head, unpad_jwt_payload, verify_jws, decrypt_jwe
from spid_cie_oidc.authority.views import trust_mark_status
from spid_cie_oidc.authority.validators import validate_entity_configuration
from spid_cie_oidc.provider.schemas.authn_requests import AuthenticationRequestSpid
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationResponse
from spid_cie_oidc.provider.schemas.authn_response import AuthenticationErrorResponse
from spid_cie_oidc.provider.schemas.introspection_request import IntrospectionRequest
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionResponse
from spid_cie_oidc.provider.schemas.introspection_response import IntrospectionErrorResponseSpid
from spid_cie_oidc.entity.schemas.op_metadata import OPMetadataSpid, OPMetadataCie
from spid_cie_oidc.entity.schemas.rp_metadata import RPMetadataSpid,RPMetadataCie
from spid_cie_oidc.provider.schemas.revocation_request import RevocationRequest
from spid_cie_oidc.provider.schemas.token_requests import TokenAuthnCodeRequest
from spid_cie_oidc.provider.schemas.token_response import TokenResponse
from spid_cie_oidc.provider.schemas.token_response import TokenErrorResponse

from spid_cie_oidc.provider.schemas.token_requests import TokenRefreshRequest
from spid_cie_oidc.provider.schemas.token_response import TokenRefreshResponse

from spid_cie_oidc.provider.schemas.jwt import JwtStructure
from spid_cie_oidc.entity.policy import apply_policy

from spid_cie_oidc.relying_party.settings import RP_PROVIDER_PROFILES
from spid_cie_oidc.provider.settings import OIDCFED_PROVIDER_PROFILES
from spid_cie_oidc.entity.views import resolve_entity_statement


def onboarding_landing(request):  # pragma: no cover
    return render(request, "onboarding_landing.html")


def onboarding_registration(request):
    form = OnboardingRegistrationForm()
    context = {"form": form}
    if request.method == "POST":
        form = OnboardingRegistrationForm(request.POST)
        if not form.is_valid():
            context = {"form": form}
        else:
            form_dict = {**form.cleaned_data}
            OnBoardingRegistration.objects.create(**form_dict)
            messages.success(request, _("Registration successfully"))
            return redirect("oidc_onboarding_entities")
    return render(request, "onboarding_registration.html", context)


def onboarding_entities(request):
    entity_list = OnBoardingRegistration.objects.all()
    p = Paginator(entity_list, 10)
    page = request.GET.get("page")
    entities = p.get_page(page)
    return render(
        request,
        "onboarding_entities.html",
        {"entity_list": entity_list, "entities": entities},
    )


def onboarding_create_jwk(request):
    _rsa_key = new_rsa_key()
    private_jwk = serialize_rsa_key(_rsa_key.priv_key, 'private')
    public_jwk = serialize_rsa_key(_rsa_key.pub_key)
    context = {
        "private_jwk": json.dumps(private_jwk, indent=4),
        "public_jwk": json.dumps(public_jwk, indent=4)
    }
    return render(request, 'onboarding_jwk.html', context)


def onboarding_convert_jwk(request):
    jwk_type = request.GET.get('type')
    context = {
        "jwk": "",
        "pem": "",
        "jwk_type": jwk_type
    }
    if request.method == 'POST':
        try:
            jwk_str = request.POST.get('jwk')
            jwk_str_double_quote = jwk_str.replace("'", '"')
            jwk_dict = json.loads(jwk_str_double_quote)

            if jwk_type == 'private':
                pem = private_pem_from_jwk(jwk_dict)
            if jwk_type == 'public':
                pem = public_pem_from_jwk(jwk_dict)

            context = {
                "jwk": jwk_dict,
                "pem": pem,
                "jwk_type": jwk_type
            }
        except Exception as e:
            messages.error(request, _(f" {e} "))
    return render(request, 'onboarding_convert_jwk.html', context)


def onboarding_convert_pem(request):
    pem_type = request.GET.get('type')
    context = {
        "pem_type": pem_type
    }
    if request.method == 'POST':
        try:
            pem = request.POST.get('pem')
            if pem_type == 'private':
                jwk = private_jwk_from_pem(pem)
            if pem_type == 'public':
                jwk = public_jwk_from_pem(pem)
            context = {
                "pem": pem,
                "pem_type": pem_type,
                "jwk": jwk
            }
        except Exception as e:
            messages.error(request, _(f" {e} "))
    return render(request, 'onboarding_convert_pem.html', context)


def onboarding_resolve_statement(request):
    if "sub" in request.GET :
        form = OnboardingCreateTrustChain(request.GET)
    else:
        form = OnboardingCreateTrustChain()
    context = {'form': form}

    if form.is_valid():
        context = {
            'form': form,
            "resolved_statement": "",
        }
        try:
            res = resolve_entity_statement(request, format="json")
            resultJson = json.loads(res.content.decode())
            context["resolved_statement"] = json.dumps(resultJson, indent=4)
        except Exception:
            messages.error(request, _('Failed to resolve entity statement, Please check your inserted data'))
    return render(request, 'onboarding_resolve_statement.html', context)


def onboarding_validating_trustmark(request):
    if "id" in request.POST or "trust_mark" in request.POST:
        form = OnboardingValidatingTrustMarkForm(request.POST)
    else:
        form = OnboardingValidatingTrustMarkForm()

    context = {"form": form}

    if form.is_valid():
        res = trust_mark_status(request)
        content = json.loads(res.content.decode())
        context = {'form': form}
        if content['active']:
            messages.success(request, _('Validation Trust Mark Successfully'))
        else:
            messages.error(request, _('Validation Trust Mark Failed'))
    return render(request, 'onboarding_validating_tm.html', context)


def onboarding_validate_md(request):
    metadata_type = request.GET.get('metadata_type')
    provider_profile = request.GET.get('provider_profile')
    md_type = metadata_type.replace("_", " ")
    title = f'Validate {md_type} {provider_profile}'
    description = f'Enter a {md_type} of {provider_profile} to verify if it is compatible'
    context = {
        "metadata_type": metadata_type,
        "provider_profile": provider_profile,
        "title": title,
        "description": description,
        "field_name":"metadata"
    }
    if request.POST.get('md'):
        md = request.POST['md']
        context["md"] = md
        try:
            md_str_double_quote = md.replace("'", '"')
            metadata = json.loads(md_str_double_quote)
            if metadata_type == 'op_metadata':
                schema = OIDCFED_PROVIDER_PROFILES[provider_profile]
                schema[metadata_type](**metadata)
                messages.success(request, _('Validation Metadata Successfully'))
            if metadata_type == 'rp_metadata':
                schema = RP_PROVIDER_PROFILES[provider_profile]
                schema[metadata_type](**metadata)
                messages.success(request, _('Validation Metadata Successfully'))
        except Exception as e:
            messages.error(request, f"Validation Failed: {e}")
    return render(request, 'onboarding_validate_md.html', context)


def onboarding_validate_authn_request(request):
    provider_profile = request.GET.get('provider_profile')
    title = f'Validate authn request {provider_profile}'
    description = f'Enter a jwt of authn request for {provider_profile} to verify if it is compatible'
    context = {
        "provider_profile": provider_profile,
        "title": title,
        "description": description,
        "field_name":"jwt"
    }
    if request.POST.get('md'):
        jwt_str = request.POST['md']
        context = {
            "provider_profile": provider_profile,
            "title": title,
            "description": description,
            "field_name":"jwt",
            "md": jwt_str
        }
        payload = unpad_jwt_payload(jwt_str)
        schema = OIDCFED_PROVIDER_PROFILES[provider_profile]
        try:
            schema["authorization_request"](**payload)
            messages.success(request, _('Validation Authn Request Successfully'))
        except Exception as e:
            messages.error(request, f"Validation Failed: {e}")
    return render(request, 'onboarding_validate_md.html', context)


def onboarding_validate_ec(request):
    context = {}
    if request.POST:
        url = request.POST.get("url")
        context = {"url": url}
        try:
            ec = validate_entity_configuration(url)
            context["ec"] = json.dumps(ec.payload, indent=4)
            messages.success(request, _('Validation Entity Configuration Successfully'))
        except Exception as e :
            messages.error(request, f"Validation Failed: {e}")
            return render(request, 'onboarding_validate_ec.html', context)
    return render(request, 'onboarding_validate_ec.html', context)


def onboarding_decode_jwt(request):
    if request.method == "GET":
        form = OnboardingDecodeForm()
    else:
        form = OnboardingDecodeForm(request.POST)

    context = {'form': form}

    if form.is_valid():
        form_dict = {**form.cleaned_data}
        jwt = form_dict['jwt']
        try:
            head = unpad_jwt_head(jwt)
        except Exception as e:
            messages.error(
                request,
                f"JWS verification failed due to missing JWT header: {e}"
            )
            return render(request, "onboarding_decode_jwt.html", context)

        if head.get('enc', None):
            if not form_dict.get('jwk'):
                messages.error(
                    request,
                    f"JWE needs a private jwk to be decrypted"
                )
                return render(
                    request, "onboarding_decode_jwt.html", context, status = 400
                )
            # JWE here
            jwk = form_dict['jwk']
            jwt = decrypt_jwe(jwt, jwk)

        try:

            payload = unpad_jwt_payload(jwt)
            context["head"] = json.dumps(head, indent=4)
            context["payload"] = json.dumps(payload, indent=4)
            jwk = form_dict["jwk"]
            if jwk:
                verify_jws(jwt, jwk)
                messages.success(request, _('Your jws is verified'))
        except Exception as e:
            messages.error(request, f"JWS verification failed: {e}")

    return render(request, "onboarding_decode_jwt.html", context)


def onboarding_apply_policy(request):
    context = {
        "md": "",
        "policy": "",
        "result": ""
    }
    if request.GET.get('md') and request.GET.get('policy'):
        context = {
                "md": request.GET['md'],
                "policy": request.GET['policy'],
                "result": ""
        }
        try:
            md = json.loads(request.GET['md'])
            policy = json.loads(request.GET['policy'])
            reuslt = apply_policy(md, policy)
            context["result"] = json.dumps(reuslt, indent=4)
        except Exception as e:
            messages.error(request, {e})
    return render(request, 'onboarding_apply_policy.html', context)


def onboarding_schemas_authorization(request):
    auth_request = AuthenticationRequestSpid.schema_json(indent=2)
    auth_res_succ = AuthenticationResponse.schema_json(indent=2)
    auth_res_err = AuthenticationErrorResponse.schema_json(indent=2)
    content = {
        "title": "Schemas authorization endpoint",
        "schemas": {
            "authorization request": auth_request,
            "authorization successful response": auth_res_succ,
            "authorization error response": auth_res_err,
        }
    }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_introspection(request):
    intro_request = IntrospectionRequest.schema_json(indent=2)
    intro_res_succ = IntrospectionResponse.schema_json(indent=2)
    intro_res_err = IntrospectionErrorResponseSpid.schema_json(indent=2)
    content = {
        "title": "Schemas introspection endpoint",
        "schemas": {
            "introspection request": intro_request,
            "introspection successful response": intro_res_succ,
            "introspection error response": intro_res_err,
        }
    }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_federation_entity_endpoints(request):
    federation_entity_fetch_request = FetchRequest.schema_json(indent=2)
    federation_entity_list_request = ListRequest.schema_json(indent=2)
    federation_entity_list_response = ListResponse.schema_json(indent=2)
    federation_entity_resolve_request = ResolveRequest.schema_json(indent=2)
    federation_entity_resolve_response = ResolveResponse.schema_json(indent=2)
    federation_entity_status_request = TrustMarkRequest.schema_json(indent=2)
    federation_entity_status_response = TrustMarkResponse.schema_json(indent=2)
    content = {
        "title": "Schemas Federation entity endpoint",
        "schemas": {
            "Federation entity fetch": federation_entity_fetch_request,
            "Federation entity list request": federation_entity_list_request,
            "Federation entity list response": federation_entity_list_response,
            "Federation entity resolve request": federation_entity_resolve_request,
            "Federation entity resolve response": federation_entity_resolve_response,
            "Federation entity status request": federation_entity_status_request,
            "Federation entity status response": federation_entity_status_response
        }
    }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_metadata(request):
    op_meta_spid = OPMetadataSpid.schema_json(indent=2)
    op_meta_cie = OPMetadataCie.schema_json(indent=2)
    rp_meta_spid = RPMetadataSpid.schema_json(indent=2)
    rp_meta_cie = RPMetadataCie.schema_json(indent=2)
    fed_entity = FAMetadata.schema_json(indent=2)
    content = {
        "title": "Schemas metadata Spid/Cie",
        "schemas": {
            "Federation entity": fed_entity,
            "OP Spid": op_meta_spid,
            "OP Cie": op_meta_cie,
            "RP Spid": rp_meta_spid,
            "RP Cie": rp_meta_cie
         }
     }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_revocation(request):
    revoc_request = RevocationRequest.schema_json(indent=2)
    content = {
        "title": "Schemas revocation endpoint",
        "schemas": {
            "revocation request": revoc_request
        }
    }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_token(request):
    auth_code_req = TokenAuthnCodeRequest.schema_json(indent=2)
    auth_code_res = TokenResponse.schema_json(indent=2)
    refr_req = TokenRefreshRequest.schema_json(indent=2)
    refr_res = TokenRefreshResponse.schema_json(indent=2)
    err_res = TokenErrorResponse.schema_json(indent=2)
    content = {
        "title": "Schemas token endpoint",
        "schemas": {
            "token authn code request": auth_code_req,
            "token authn code response": auth_code_res,
            "refresh token request": refr_req,
            "refresh token response": refr_res,
            "token error response": err_res
        }
    }
    return render(request, "onboarding_schemas.html", content)


def onboarding_schemas_jwt_client_assertion(request):
    jwt_client_asser = JwtStructure.schema_json(indent=2)
    content = {
        "title": "Schemas jwt",
        "schemas": {
            "jwt client assertion": jwt_client_asser
        }
    }
    return render(request, "onboarding_schemas.html", content)
