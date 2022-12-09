import json
import logging
import requests
import uuid

from spid_cie_oidc.entity.models import FederationEntityConfiguration
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.settings import HTTPC_PARAMS, HTTPC_TIMEOUT
from spid_cie_oidc.entity.utils import iat_now, exp_from_now

logger = logging.getLogger(__name__)


class OAuth2AuthorizationCodeGrant(object):
    """
    https://tools.ietf.org/html/rfc6749
    """

    def access_token_request(
        self,
        redirect_uri: str,
        state: str,
        code: str,
        issuer_id: str,
        client_conf: FederationEntityConfiguration,
        token_endpoint_url: str,
        audience: list,
        code_verifier: str = None,
    ):
        """
        Access Token Request
        https://tools.ietf.org/html/rfc6749#section-4.1.3
        """
        grant_data = dict(
            grant_type="authorization_code",
            redirect_uri=redirect_uri,
            client_id=client_conf.sub,
            state=state,
            code=code,
            code_verifier=code_verifier,
            # here private_key_jwt
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            client_assertion=create_jws(
                {
                    "iss": client_conf.sub,
                    "sub": client_conf.sub,
                    "aud": [token_endpoint_url],
                    "iat": iat_now(),
                    "exp": exp_from_now(),
                    "jti": str(uuid.uuid4()),
                },
                jwk_dict=client_conf.jwks_core[0],
            ),
        )

        logger.debug(f"Access Token Request for {state}: {grant_data} ")
        token_request = requests.post(
            token_endpoint_url,
            data=grant_data,
            verify=HTTPC_PARAMS["connection"]["ssl"],
            timeout=HTTPC_TIMEOUT,
        )

        if token_request.status_code != 200: # pragma: no cover
            logger.error(
                f"Something went wrong with {state}: {token_request.status_code}"
            )
        else:
            try:
                token_request = json.loads(token_request.content.decode())
            except Exception as e:  # pragma: no cover
                logger.error(f"Something went wrong with {state}: {e}")
        return token_request
