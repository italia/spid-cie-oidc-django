import hashlib


def spidCode(user_info: dict, client_conf: dict, data: dict = None, kwargs: dict = {}):

    return hashlib.sha512(
        f"{user_info['username']}{kwargs.get('salt', '')}".encode()
    ).hexdigest()
