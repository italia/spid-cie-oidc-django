
from django.shortcuts import redirect, render
from pydantic import ValidationError
from spid_cie_oidc.entity.jwtse import (unpad_jwt_head, unpad_jwt_payload,
                                        verify_jws)
from spid_cie_oidc.entity.models import TrustChain
from spid_cie_oidc.entity.tests.settings import *
from spid_cie_oidc.onboarding.schemas.authn_requests import \
    AuthenticationRequestSpid


def authn_request(request):
    req = request.GET.get('request', None)
    try:
        payload = unpad_jwt_payload(req)
        header = unpad_jwt_head(req)
        rp_trust_chain = TrustChain.objects.filter(type = "openid_relying_party", sub= payload['iss']).first()
        
        if not rp_trust_chain.is_valid:
            # response error ???
            error_description = ""
            error = ""
            return redirect_error_response(payload, error, error_description)
        
        if not rp_trust_chain.is_active:
            # gli rispondo con error response con access_denied??????
            error_description = ""
            error = ""
            return redirect_error_response(payload, error, error_description)
        
        if not rp_trust_chain.is_expired:
            #rinnova truest_chain
             pass
        
        jwks = rp_trust_chain.metadata['jwks']
        jwk = find_jwk(header, jwks)
        if not jwk:
            # torno una response error con unauthorized_client????
            error_description = ""
            error = ""
            return redirect_error_response(payload, error, error_description)
        
        try:
            verify_jws(request.GET["request"], jwk)
            try:
                AuthenticationRequestSpid(**payload)
                return render(request, "login_rp.html")
                # return reneder (template logging page) e gli passo anche il dict della request
            except ValidationError as exc:
                #invalid_request
                error_description = ""
                error = ""
                return redirect_error_response(payload, error, error_description)
        except Exception as exc:
            #torno una response error con unauthorized_client
            error_description = ""
            error = ""
            return redirect_error_response(payload, error, error_description)
    
    except Exception as exc:
        # gli rispondo con error response con invalid_request??????
        error_description = ""
        error = ""
        return redirect_error_response(payload, error, error_description)


def build_error_response(error, error_description, state): 
    return dict(
        error_description = error_description,
        error = error,
        state = state,
        )

def redirect_error_response(payload, error, error_description):
    redirect_uri = payload['redirect_uri']
    state = payload['state']
    response = build_error_response(error, error_description, state)
    return redirect(redirect_uri, **response)
    
    #check
    # unpad payload di request.GET.get(request, None)
    # unpad header di request.GET.get(request, None)
    #se schifezza try?????
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

def find_jwk(header, jwks):
    for jwk in jwks:
        if header['kid'] == jwk['kid']:
            return jwk


def user_login(request):
    pass
#from django.contrib.auth import authenticate
# request.POST lo do a dezhi se è valido faccio authenticate
# form.cleanedData
       # user = authenticate(username=username,
        #                    password=password)
       #se va male si ritorna form con errore o password errata
       # se va tutto bene 
       # creo la session con il jwt dal form 
       # creo un altro web point
       # faccio redirect su user_content

# @login_required
#  def user_content():
 