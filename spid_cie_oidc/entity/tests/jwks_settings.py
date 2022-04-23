from copy import deepcopy

JWKS = {
    "keys": [
        {
            "kty": "EC",
            "kid": "sig-ec256-0",
            "use": "sig",
            "crv": "P-256",
            "x": "2jM2df3IjB9VYQ0yz373-6EEot_1TBuTRaRYafMi5K0",
            "y": "h6Zlz6XReK0L-iu4ZgxlozJEXgTGUFuuDl7o8b_8JnM",
        },
        {
            "kty": "EC",
            "kid": "enc-ec256-1",
            "use": "enc",
            "crv": "P-256",
            "x": "QI31cvWP4GwnWIi-Z0IYHauQ4nPCk8Vf1BHoPazGqEc",
            "y": "DBwf8t9-abpXGtTDlZ8njjxAb33kOMrOqiGsd9oRxr0",
        },
    ]
}

JWKS_WITH_N_AND_EC_NO_CORRECT = deepcopy(JWKS)
JWKS_WITH_N_AND_EC_NO_CORRECT["keys"][0][
    "n"
] = "iu4ZgxlozJEXgTGUFuuDl7o8b_8JnMswwddaQjhFkKk"

JWKS_WITH_X_AND_RSA_NO_CORRECT = deepcopy(JWKS)
JWKS_WITH_X_AND_RSA_NO_CORRECT["keys"][0][
    "x"
] = "iu4ZgxlozJEXgTGUFuuDl7o8b_8JnMswwddaQjhFkKk"
JWKS_WITH_X_AND_RSA_NO_CORRECT["keys"][0]["kty"] = "RSA"
