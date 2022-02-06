import base64
import json
import hashlib
import logging
import os
import random
import re
import string
import urllib


from cryptojwt import KeyJar
from cryptojwt.key_jar import KeyJar
from django.utils.safestring import mark_safe
from oidcmsg.message import Message


logger = logging.getLogger(__name__)


def http_redirect_uri_to_dict(url):
    splitted = urllib.parse.splitquery(url)
    data = dict(urllib.parse.parse_qsl(splitted[1]))
    data.update({'endpoint': splitted[0]})
    return data


def http_dict_to_redirect_uri_path(data):
    return urllib.parse.urlencode(data)


def decode_token(bearer_token, keyjar, verify_sign=True):
    msg = Message().from_jwt(bearer_token,
                             keyjar=keyjar,
                             verify=verify_sign)
    return msg.to_dict()


def random_string(n=27):
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=n)
    )


def get_pkce(code_challenge_method: str = 'S256',
             code_challenge_length: int = 64):
    hashers = {
        'S256': hashlib.sha256
    }

    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

    code_challenge = hashers.get(code_challenge_method)(
        code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    return {
        'code_verifier': code_verifier,
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method
    }


def get_issuer_keyjar(jwks, issuer: str):
    key_jar = KeyJar()
    # "" means default, you can always point to a issuer identifier
    key_jar.import_jwks(jwks, issuer_id=issuer)
    return key_jar


def validate_jwt(jwt: str, key_jar):
    try:
        recv = Message().from_jwt(jwt, keyjar=key_jar)
        return recv.verify(), key_jar
    except:
        return False


def html_json_preview(value):
    msg = json.loads(value or '{}')
    dumps = json.dumps(msg, indent=2)
    return mark_safe(dumps.replace('\n', '<br>').replace('\s', '&nbsp'))
