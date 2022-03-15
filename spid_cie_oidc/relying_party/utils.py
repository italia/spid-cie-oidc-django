import base64
import json
import hashlib
import logging
import os
import random
import re
import string
import urllib


from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe


logger = logging.getLogger(__name__)


def http_redirect_uri_to_dict(url):
    splitted = urllib.parse.splitquery(url)
    data = dict(urllib.parse.parse_qsl(splitted[1]))
    data.update({"endpoint": splitted[0]})
    return data


def http_dict_to_redirect_uri_path(data):
    return urllib.parse.urlencode(data)


def random_string(n=32):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))  # nosec


def get_pkce(code_challenge_method: str = "S256", code_challenge_length: int = 64):
    hashers = {"S256": hashlib.sha256}

    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    code_challenge = hashers.get(code_challenge_method)(
        code_verifier.encode("utf-8")
    ).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    return {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }


def html_json_preview(value):
    msg = json.loads(value or "{}")
    dumps = json.dumps(msg, indent=2)
    return mark_safe(dumps.replace("\n", "<br>").replace(" ", "&nbsp"))  # nosec


def process_user_attributes(userinfo: dict, user_map: dict, authz: dict):
    data = dict()
    for k, v in user_map.items():
        for i in v:
            if isinstance(i, str):
                if i in userinfo:
                    data[k] = userinfo[i]
                    break

            elif isinstance(i, dict):
                args = (userinfo, authz, i["kwargs"])
                value = import_string(i["func"])(*args)
                if value:
                    data[k] = value
                    break
    return data
