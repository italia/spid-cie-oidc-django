from secrets import token_hex


def random_token(n=254):
    return token_hex(n)
