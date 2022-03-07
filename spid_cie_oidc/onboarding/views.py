import json
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
