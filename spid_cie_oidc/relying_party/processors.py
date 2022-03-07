def issuer_prefixed_sub(
    user_info: dict, client_conf: dict, data: dict = None, kwargs: dict = {}
):
    return f"{client_conf['provider_id']}{data.get('sep', '__')}{user_info['sub']}"
