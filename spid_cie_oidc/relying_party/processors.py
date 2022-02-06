def issuer_prefixed_sub(user_info:dict,
                        client_conf:dict,
                        data:dict=None,
                        kwargs:dict={}):
    return f"{data['issuer_id']}{kwargs.get('sep', '__')}{user_info['sub']}"
