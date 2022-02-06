import json
import logging
import requests

from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


class OAuth2AuthorizationCodeGrant(object):
    """
        https://tools.ietf.org/html/rfc6749#section-1.3.1
        https://tools.ietf.org/html/rfc6749#section-4.1
    """
    def get_token_endpoint_auth_method(self,
                                       client_conf: dict,
                                       grant_data:dict = {},
                                       method: str = None):
        method = method or client_conf['client_preferences']['token_endpoint_auth_method'][0]

        if all((method == 'client_secret_basic',
                'client_secret' in client_conf)):
            auth = HTTPBasicAuth(
                client_conf['client_id'],
                client_conf['client_secret']
            )
            data = {'auth': auth, 'data': grant_data}
            return data
        elif method == 'client_secret_post':
            grant_data.update({
                'client_id' : client_conf['client_id'],
                'client_secret' : client_conf['client_secret']
            })
            return grant_data

    def access_token_request(self,
                             redirect_uri:str,
                             client_id:str,
                             state:str,
                             code:str,
                             issuer_id:str,
                             client_conf:dict,
                             token_endpoint_url:str,
                             code_verifier:str = None):
        """
        Access Token Request
        https://tools.ietf.org/html/rfc6749#section-4.1.3
        """
        grant_data = dict(
            grant_type='authorization_code',
            redirect_uri = redirect_uri,
            client_id = client_id,
            state = state,
            code = code,
        )

        if code_verifier:
            grant_data.update({'code_verifier': code_verifier})

        issuer_id = issuer_id
        token_req_data = self.get_token_endpoint_auth_method(
            client_conf, grant_data
        )
        logger.debug(f'Access Token Request for {state}: {token_req_data} ')

        token_request = requests.post(
                token_endpoint_url,
                **token_req_data,
                verify=client_conf['httpc_params']['verify']
        )

        if token_request.status_code != 200:
            logger.error(
                f'Something went wrong with {state}: {token_request.content}')
        else:
            try:
                token_request = json.loads(token_request.content.decode())
                return token_request
            except Exception as e: # pragma: no cover
                logger.error(f'Something went wrong with {state}: {e}')
        return token_request
