from django.http import Http403
from django.views import View
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from pydantic import ValidationError
from spid_cie_oidc.entity.jwtse import (
    unpad_jwt_head, unpad_jwt_payload,
    verify_jws
)
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.onboarding.schemas.authn_requests import AuthenticationRequestSpid

from . forms import *


class OpBase:
    """
        Baseclass with common methods for OPs
    """

    def handle_json_error(
            self, error:str, error_description:str, state:str
    ) -> dict:

        return dict(
            error_description = error_description,
            error = error,
            state = state,
        )

    def find_jwk(self, header:dict, jwks:list) -> dict:
        for jwk in jwks:
            if header['kid'] == jwk['kid']:
                return jwk

    def validate_authz_request_object(self, req):
        try:
            payload = unpad_jwt_payload(req)
            header = unpad_jwt_head(req)
        except Exception as e:
            logger.error(
                f"Error in Authz request object {dict(request.GET)}: {e}"
            )
            # TODO: render an error template here
            return HttpResponse(
                _("Authorization Request is not valid.")
            )

        trust_chain = TrustChain.objects.filter(
            type = "openid_relying_party",
            sub = payload['iss']
        ).first()

        if trust_chain and not trust_chain.is_active:
            logger.warning(
                f"Disabled client {trust_chain.sub} requests an authorization."
            )
            raise Http403()

        elif not trust_chain or not rp_trust_chain.is_valid:
            trust_chain = get_or_create_trust_chain(
                subject = payload['iss'],
                trust_anchor = settings.OIDCFED_FEDERATION_TRUST_ANCHOR,
                metadata_type = 'openid_relying_party',
                httpc_params = HTTPC_PARAMS,
                required_trust_marks = getattr(
                    settings, 'OIDCFED_REQUIRED_TRUST_MARKS', []
                )
            )
            if not tc.is_valid:
                logger.warning(
                    f"Failed trust chain validation for {payload['iss']}"
                )
                raise Http403()

        jwks = rp_trust_chain.metadata['jwks']
        jwk = self.find_jwk(header, jwks)
        if not jwk:
            logger.error(
                f"Invalid jwk for {payload['iss']}. "
                f"{header['kid']} not found in {jwks}"
            )
            raise Http403()

        try:
            verify_jws(req, jwk)
        except Exception as e:
            logger.error(
                "Authz request object signature validation failed "
                f"for {payload['iss']}: {e} "
            )
            raise Http403()

        return payload


class AuthzRequestView(OpBase, View):
    """View which processes the actual Authz request and
    returns a Http Redirect
    """
    template = "op_user_login.html"

    def get(self, request, *args, **kwargs):
        """
            authz request object is received here
            it's validated and a login prompt is rendered to the user
        """
        req = request.GET.get('request', None)
        if not req:
            logger.error(
                f"Missing Authz request object in {dict(request.GET)}"
            )
            # TODO: render an error template here
            return HttpResponse(
                _("Authorization Request not found.")
            )
        authz_req = self.validate_authz_request_object(req)

        try:
            AuthenticationRequestSpid(**payload)
        except ValidationError:
            logger.error(
                "Authz request object validation failed "
                f"for {authz_req['iss']}: {e} "
            )
            raise Http403()

        # stores the authz request in a hidden field in the form
        context = {
            "form": AuthLoginForm(authz_request_object=req)
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
            When the User prompts his credentials
        """
        form = AuthLoginForm(request.POST)
        if not form.is_valid():
            return render(request, "login_rp.html", {'form': form})

        self.validate_authz_request_object(req)

        # autenticate the user

        #from django.contrib.auth import authenticate
        # request.POST lo do a dezhi se è valido faccio authenticate
        # form.cleanedData
        # user = authenticate(username=username,
        #                    password=password)
        # se va male si ritorna form con errore o password errata
        # se va tutto bene
        # creo la session con il jwt dal form
        # creo un altro web point
        # faccio redirect su user_content

        # store the User session
        # redirect the user to a consent page

        redirect_uri = payload['redirect_uri']
        state = payload['state']
        response = build_error_response(error, error_description, state)
        return redirect(redirect_uri, **response)

        # check
        # unpad payload di request.GET.get(request, None)
        # unpad header di request.GET.get(request, None)
        # se schifezza try?????
        # devo fare query su entity.models.trust_chain.objects.filter(type ="openid_relayparty", sub= payload[iss]).first()
        # se mi rende oggetto e foggetto.isActive() == true controlla isExpired
        # se scaduto rinnopva trust_chain
        # altrimenti valido jwt: trust_chain.metadata[jwks]
        # for jwk : in trust_chain.metadata[jwks]:
        #   if header[kid] == jwk:
        #       entity.jwtse.validate_...(request.GET["request"]) se fallisce nell'except torno una response error con unauthorized_client

        #   return redirect HttpsResponse
        # altrimente devo validare il payload con json schema
        # se non è valido gli rispondo con error response e invalid_request
        #
        # se è valido
        # return reneder (template logging page) e gli passo anche il dict della request


class ConsentPageView(View):
    # create a redirect with auth code, scope, state and iss in it
    template = "op_user_consent.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http403()

        # TODO: create a form with the consent submission
        # stores the authz request in a hidden field in the form
        context = {
            # "form": ConsentPageForm()
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http403()

        # TODO: create a form with the consent submission
        # stores the authz request in a hidden field in the form
        form = ConsentPageForm(request.POST)
        if not form.is_valid():
            # user doesn't give his consent, redirect to an error page
            raise Http403()

        context = {"form": form}
        return render(request, self.template, context)


class TokenEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class UserInfoEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class IntrospectionEndpoint(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
