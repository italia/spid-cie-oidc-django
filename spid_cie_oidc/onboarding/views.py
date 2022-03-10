import json
from textwrap import indent
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _

from .forms import (
    OnboardingRegistrationForm,
    OnboardingCreateTrustChain,
    OnboardingValidatingTrustMarkForm
)
from .models import OnBoardingRegistration
from spid_cie_oidc.entity.jwks import (
    private_pem_from_jwk,
    public_pem_from_jwk,
    new_rsa_key,
    serialize_rsa_key
)

from spid_cie_oidc.entity.jwtse import unpad_jwt_head, unpad_jwt_payload, verify_jws
from spid_cie_oidc.authority.views import trust_mark_status, resolve_entity_statement
from spid_cie_oidc.onboarding.schemas.authn_requests import AuthenticationRequestSpid
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationResponse
from spid_cie_oidc.onboarding.schemas.authn_response import AuthenticationErrorResponse
from spid_cie_oidc.onboarding.schemas.introspection_request import IntrospectionRequest
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionResponse
from spid_cie_oidc.onboarding.schemas.introspection_response import IntrospectionErrorResponseSpid
from spid_cie_oidc.entity.schemas.op_metadata import OPMetadataSpid, OPMetadataCie
from spid_cie_oidc.entity.schemas.rp_metadata import RPMetadataSpid,RPMetadataCie
from spid_cie_oidc.onboarding.schemas.revocation_request import RevocationRequest
from spid_cie_oidc.onboarding.schemas.token_requests import TokenAuthnCodeRequest
from spid_cie_oidc.onboarding.schemas.token_response import TokenResponse
from spid_cie_oidc.onboarding.schemas.token_response import TokenErrorResponse

from spid_cie_oidc.onboarding.schemas.token_requests import TokenRefreshRequest
from spid_cie_oidc.onboarding.schemas.token_response import TokenRefreshResponse

from spid_cie_oidc.onboarding.schemas.jwt import JwtStructure


def onboarding_landing(request):
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
        "private_jwk": private_jwk,
        "public_jwk": public_jwk
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
    return render(request, 'onboarding_convert_jwk.html', context)


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
            context["resolved_statement"] = res.content.decode()
        except Exception:
            messages.error(request, _('Failed to resolve entity statement, Please check your inserted data'))
            render(request, 'onboarding_resolve_statement.html', context)

    return render(request, 'onboarding_resolve_statement.html', context)


def onboarding_validating_trustmark(request):
    if "id" in request.GET or "trust_mark" in request.GET:
        form = OnboardingValidatingTrustMarkForm(request.GET)
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


def onboarding_decode_jwt(request):
    context = {
            "jwt": "",
            "jwk": "",
            "head": "",
            "payload": ""
    }
    if request.POST.get('jwt'):
        jwt = request.POST['jwt']
        head = unpad_jwt_head(jwt)
        payload = unpad_jwt_payload(jwt)
        context["jwt"] = jwt
        context["head"] = head
        context["payload"] = payload
        if request.POST.get('jwk'):
            jwk_str = request.POST['jwk']
            context["jwk"] = jwk_str
            jwk_str_double_quote = jwk_str.replace("'", '"')
            jwk = json.loads(jwk_str_double_quote)
            try:
                verify_jws(jwt, jwk)
                messages.success(request, _('Your jws is verified'))
            except Exception:
                messages.error(request, _("Jws verification failed"))
                render(request, 'onboarding_decode_jwt.html', context)
    return render(request, 'onboarding_decode_jwt.html', context)


def onboarding_schemas_authorization(request):
    auth_request = AuthenticationRequestSpid.schema_json(indent=2)
    auth_res_succ = AuthenticationResponse.schema_json(indent=2)
    auth_res_err = AuthenticationErrorResponse.schema_json(indent=2)
    content = dict(
        auth_request = auth_request,
        auth_res_succ = auth_res_succ,
        auth_res_err = auth_res_err
    )
    return render(request, "onboarding_schemas_authorization.html", content)


def onboarding_schemas_introspection(request):
    intro_request = IntrospectionRequest.schema_json(indent=2)
    intro_res_succ = IntrospectionResponse.schema_json(indent=2)
    intro_res_err = IntrospectionErrorResponseSpid.schema_json(indent=2)
    content = dict(
        intro_request = intro_request,
        intro_res_succ = intro_res_succ,
        intro_res_err = intro_res_err
    )
    return render(request, "onboarding_schemas_introspection.html", content)


def onboarding_schemas_metadata(request):
    op_meta_spid = OPMetadataSpid.schema_json(indent=2)
    op_meta_cie = OPMetadataCie.schema_json(indent=2)
    rp_meta_spid = RPMetadataSpid.schema_json(indent=2)
    rp_meta_cie = RPMetadataCie.schema_json(indent=2)
    content = dict(
        op_meta_spid = op_meta_spid,
        op_meta_cie = op_meta_cie,
        rp_meta_spid = rp_meta_spid,
        rp_meta_cie = rp_meta_cie
    )
    return render(request, "onboarding_schemas_metadata.html", content)


def onboarding_schemas_revocation(request):
    revoc_request = RevocationRequest.schema_json(indent=2)
    content = dict(
        revoc_request = revoc_request,
    )
    return render(request, "onboarding_schemas_revocation.html", content)


def onboarding_schemas_token(request):
    auth_code_req = TokenAuthnCodeRequest.schema_json(indent=2)
    auth_code_res = TokenResponse.schema_json(indent=2)
    refr_req = TokenRefreshRequest.schema_json(indent=2)
    refr_res = TokenRefreshResponse.schema_json(indent=2)
    err_res = TokenErrorResponse.schema_json(indent=2)
    content = dict(
        auth_code_req = auth_code_req,
        auth_code_res = auth_code_res,
        refr_req = refr_req,
        refr_res = refr_res,
        err_res = err_res
    )
    return render(request, "onboarding_schemas_token.html", content)


def onboarding_schemas_jwt_client_assertion(request):
    jwt_client_asser = JwtStructure.schema_json(indent=2)
    content = dict(
        jwt_client_asser = jwt_client_asser,
    )
    return render(request, "onboarding_schemas_jwt_client_assertion.html", content)
