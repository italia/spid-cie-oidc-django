from cryptojwt.jwk.rsa import new_rsa_key


def create_jwk():
    return new_rsa_key().serialize('private')
