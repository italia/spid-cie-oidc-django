import logging
import uuid
from cryptojwt.jws.utils import left_hash
from django.conf import settings
from pydantic import ValidationError
from django.http import HttpResponseRedirect
from django.utils import timezone
import urllib
from spid_cie_oidc.entity.jwtse import create_jws, unpad_jwt_head, unpad_jwt_payload, verify_jws
from spid_cie_oidc.entity.models import FederationEntityConfiguration, TrustChain
from spid_cie_oidc.entity.settings import HTTPC_PARAMS
from spid_cie_oidc.entity.trust_chain_operations import get_or_create_trust_chain
from spid_cie_oidc.entity.utils import datetime_from_timestamp, exp_from_now, iat_now
from spid_cie_oidc.entity.utils import get_jwks
from spid_cie_oidc.provider.exceptions import AuthzRequestReplay, ExpiredAuthCode, InvalidSession, RevokedSession, ValidationException
from spid_cie_oidc.provider.models import OidcSession

from spid_cie_oidc.provider.settings import (
    OIDCFED_ATTRNAME_I18N,
    OIDCFED_DEFAULT_PROVIDER_PROFILE,
    OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE,
    OIDCFED_PROVIDER_PROFILES,
    OIDCFED_PROVIDER_PROFILES_ACR_4_REFRESH,
    OIDCFED_PROVIDER_PROFILES_ID_TOKEN_CLAIMS
)
logger = logging.getLogger(__name__)


class OpBase:
    """
    Baseclass with common methods for OPs
    """

    def redirect_response_data(self, redirect_uri:str, **kwargs) -> HttpResponseRedirect:
        url = f'{redirect_uri}?{urllib.parse.urlencode(kwargs)}'
        return HttpResponseRedirect(url)

    def find_jwk(self, header: dict, jwks: list) -> dict:
        for jwk in jwks:
            if header["kid"] == jwk["kid"]:
                return jwk

    def validate_authz_request_object(self, req) -> TrustChain:
        state = getattr(self, 'payload', {}).get("state", "")
        try:
            self.payload = unpad_jwt_payload(req)
            header = unpad_jwt_head(req)
        except Exception as e:
            _msg = (
                f"Error in Authz request object {dict(req.GET)}: {e}."
                f" error=invalid_request"
                f"state={state}"
            )
            logger.error(_msg)
            raise Exception(_msg)

        self.is_a_replay_authz()
        rp_trust_chain = TrustChain.objects.filter(
            metadata__openid_relying_party__isnull=False,
            sub=self.payload["iss"],
            trust_anchor__sub=settings.OIDCFED_DEFAULT_TRUST_ANCHOR
        ).first()
        if rp_trust_chain and not rp_trust_chain.is_active:
            _msg = (
                f"Disabled client {rp_trust_chain.sub} requests an authorization. "
                "error = access_denied, "
                f"state={state}"
            )
            logger.warning(_msg)
            raise Exception(_msg)

        elif not rp_trust_chain or rp_trust_chain.is_expired:
            rp_trust_chain = get_or_create_trust_chain(
                subject=self.payload["iss"],
                trust_anchor=settings.OIDCFED_DEFAULT_TRUST_ANCHOR,
                httpc_params=HTTPC_PARAMS,
                required_trust_marks=getattr(
                    settings, "OIDCFED_REQUIRED_TRUST_MARKS", []
                ),
            )
            if not rp_trust_chain.is_valid:
                _msg = (
                    f"Failed trust chain validation for {self.payload['iss']}. "
                    "error=unauthorized_client, "
                    f"state={state}"
                )
                logger.warning(_msg)
                raise Exception(_msg)

        jwks = get_jwks(
            rp_trust_chain.metadata['openid_relying_party'],
            federation_jwks = rp_trust_chain.jwks
        )
        jwk = self.find_jwk(header, jwks)
        if not jwk:
            _msg = (
                f"Invalid jwk for {self.payload['iss']}. "
                f"{header['kid']} not found in {jwks}. "
                "error=unauthorized_client, "
                f"state={state}"
            )
            logger.error(_msg)
            raise Exception(_msg)

        try:
            verify_jws(req, jwk)
        except Exception as e:
            _msg = (
                "Authz request object signature validation failed "
                f"for {self.payload['iss']}: {e}. "
                f"error=access_denied, state={state}"
            )
            logger.error(_msg)
            raise Exception(_msg)

        return rp_trust_chain

    def is_a_replay_authz(self):
        preexistent_authz = OidcSession.objects.filter(
            client_id=self.payload["client_id"],
            nonce=self.payload["nonce"]
        ).first()
        if preexistent_authz:
            raise AuthzRequestReplay(
                f"{preexistent_authz.client_id} with {preexistent_authz.nonce}"
            )

    def check_session(self, request) -> OidcSession:
        if not request.user.is_authenticated:
            raise InvalidSession()

        auth_code = request.session.get("oidc", {}).get("auth_code", None)
        if not auth_code:
            # FIXME: to do test
            raise InvalidSession()

        session = OidcSession.objects.filter(
            auth_code=request.session["oidc"]["auth_code"]
        ).first()

        if not session:
            raise InvalidSession("Unknown Session")

        if session.user != request.user:
            raise InvalidSession(
                f"Different user, session is of {session.user} "
                f"but request user is {request.user}"
            )

        if session.revoked:
            raise RevokedSession(
                "Session was revoked"
            )

        session_not_after = session.created + timezone.timedelta(
            minutes = OIDCFED_PROVIDER_AUTH_CODE_MAX_AGE
        )
        if session_not_after < timezone.localtime():
            raise ExpiredAuthCode(
                f"The Session is expired at {session_not_after}"
            )
        return session

    def get_issuer(self):
        return FederationEntityConfiguration.objects.filter(
            entity_type="openid_provider"
        ).first()

    def check_client_assertion(self, client_id: str, client_assertion: str) -> bool:
        head = unpad_jwt_head(client_assertion)
        payload = unpad_jwt_payload(client_assertion)
        _sub = payload.get('sub', None)
        _aud = payload.get('aud', [])
        _op = self.get_issuer()
        _op_eid = _op.sub
        _op_eid_authz_endpoint = [_op.metadata['openid_provider']['authorization_endpoint']]

        if isinstance(_aud, str):
            _aud = [_aud]
        _allowed_auds = _aud + _op_eid_authz_endpoint

        if _sub != client_id:
            logger.warning(
                f"Client assertion failed: {_sub} != {client_id}"
            )
            # TODO Specialize exceptions
            raise Exception()

        if _op_eid:
            _allowed_auds.append(_op_eid)

        if not _op_eid or self.request.build_absolute_uri() not in _allowed_auds:
            logger.warning(
                "Client assertion failed, fake audience: "
                f"{self.request.build_absolute_uri()} not in {_allowed_auds}"
            )
            # TODO Specialize exceptions
            raise Exception()

        tc = TrustChain.objects.get(sub=client_id, is_active=True)
        jwk = self.find_jwk(head, tc.metadata['openid_relying_party']['jwks']['keys'])
        verify_jws(client_assertion, jwk)
        return True

    def validate_json_schema(self, payload, schema_type, error_description):
        try:
            schema = OIDCFED_PROVIDER_PROFILES[OIDCFED_DEFAULT_PROVIDER_PROFILE]
            schema[schema_type](**payload)
        except (ValidationError, Exception) as e:
            logger.error(
                f"{error_description} "
                f"for {payload.get('client_id', None)}: {e}"
            )
            raise ValidationException()

    def get_jwt_common_data(self):
        return {
            "jti": str(uuid.uuid4()),
            "exp": exp_from_now(),
            "iat": iat_now()
        }

    def get_access_token(
            self, iss_sub:str, sub:str, authz: OidcSession, commons:dict
    ) -> dict:

        access_token = {
            "iss": iss_sub,
            "sub": sub,
            "aud": [authz.client_id],
            "client_id": authz.client_id,
            "scope": authz.authz_request["scope"],
        }
        access_token.update(commons)

        return access_token

    def get_id_token_claims(
        self,
        authz:OidcSession
    ) -> dict:
        _provider_profile = getattr(settings, 'OIDCFED_DEFAULT_PROVIDER_PROFILE', OIDCFED_DEFAULT_PROVIDER_PROFILE)
        claims = {}
        allowed_id_token_claims = OIDCFED_PROVIDER_PROFILES_ID_TOKEN_CLAIMS[_provider_profile]
        if not allowed_id_token_claims:
            return claims

        for claim in (
                    authz.authz_request.get(
                        "claims", {}
                    ).get("id_token", {}).keys()
        ):
            if claim in allowed_id_token_claims and authz.user.attributes.get(claim, None):
                claims[claim] = authz.user.attributes[claim]
        return claims

    def get_id_token(
                self,
                iss_sub:str,
                sub:str,
                authz:OidcSession,
                jwt_at:str,
                commons:dict
    ) -> dict:

        id_token = {
            "sub": sub,
            "nonce": authz.authz_request["nonce"],
            "at_hash": left_hash(jwt_at, "HS256"),
            "c_hash": left_hash(authz.auth_code, "HS256"),
            "aud": [authz.client_id],
            "iss": iss_sub,
            "acr": authz.acr
        }
        claims = self.get_id_token_claims(authz)
        if claims:
            id_token.update(claims)

        id_token.update(commons)
        return id_token

    def get_refresh_token(
            self,
            iss_sub:str,
            sub:str,
            authz:OidcSession,
            jwt_at:str,
            commons:dict
    ) -> dict:
        # refresh token is scope offline_access and prompt == consent
        refresh_acrs = OIDCFED_PROVIDER_PROFILES_ACR_4_REFRESH[OIDCFED_DEFAULT_PROVIDER_PROFILE]
        acrs = authz.authz_request.get('acr_values', [])
        if (
            "offline_access" in authz.authz_request['scope'] and
            'consent' in authz.authz_request['prompt'] and
            set(refresh_acrs).intersection(set(acrs))
        ):
            refresh_token = {
                "sub": sub,
                "at_hash": left_hash(jwt_at, "HS256"),
                "c_hash": left_hash(authz.auth_code, "HS256"),
                "aud": [authz.client_id],
                "iss": iss_sub,
            }
            refresh_token.update(commons)
            return refresh_token

    def get_iss_token_data(self, session : OidcSession, issuer: FederationEntityConfiguration):
        _sub = session.pairwised_sub()
        iss_sub = issuer.sub
        commons = self.get_jwt_common_data()
        jwk = issuer.jwks_core[0]

        access_token = self.get_access_token(iss_sub, _sub, session, commons)
        jwt_at = create_jws(access_token, jwk, typ="at+jwt")
        id_token = self.get_id_token(iss_sub, _sub, session, jwt_at, commons)
        jwt_id = create_jws(id_token, jwk)

        iss_token_data = dict(
            session=session,
            access_token=jwt_at,
            id_token=jwt_id,
            expires=datetime_from_timestamp(commons["exp"])
        )

        _refresh_token = self.get_refresh_token(iss_sub, _sub, session, jwt_at, commons)
        if _refresh_token:
            jwt_rt = create_jws(_refresh_token, jwk)
            iss_token_data["refresh_token"] = jwt_rt
        return iss_token_data

    def get_expires_in(self, iat: int, exp: int):
        return timezone.timedelta(
            seconds = exp - iat
        ).seconds

    def attributes_names_to_release(self, request, session: OidcSession) -> dict:
        # get up fresh claims
        user_claims = request.user.attributes
        user_claims["email"] = user_claims.get("email", request.user.email)
        user_claims["username"] = request.user.username

        # filter on requested claims
        filtered_user_claims = {}
        for target, claims in session.authz_request.get("claims", {}).items():
            for claim in claims:
                if claim in user_claims:
                    filtered_user_claims[claim] = user_claims[claim]

        # mapping with human names
        i18n_user_claims = [
            OIDCFED_ATTRNAME_I18N.get(i, i)
            for i in filtered_user_claims.keys()
        ]
        return dict(
            i18n_user_claims = i18n_user_claims,
            filtered_user_claims = filtered_user_claims
        )
