TA_SUB = "http://testserver/"
FA_METADATA = {
    "federation_entity": {
        "contacts": ["ops@localhost"],
        "federation_fetch_endpoint": f"{TA_SUB}/fetch",
        "federation_list_endpoint": f"{TA_SUB}/list/",
        "homepage_uri": f"{TA_SUB}",
        "name": "example TA",
    }
}
TM_ISSUERS = {
    "https://www.spid.gov.it/certification/rp/public": [
        TA_SUB,
        "https://public.intermediary.spid.it",
    ],
    "https://www.spid.gov.it/certification/rp/private": [
        TA_SUB,
        "https://private.other.intermediary.it",
    ],
    "https://sgd.aa.it/onboarding": ["https://sgd.aa.it"],
}
FA_CONSTRAINTS = {"max_path_length": 1}

ta_conf_data = dict(
    sub=TA_SUB,
    metadata=FA_METADATA,
    constraints=FA_CONSTRAINTS,
    is_active=1,
    trust_marks_issuers=TM_ISSUERS,
)
TA_JWK_PRIVATE = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'd': 'jEDxjcTZXBbgBV8Bgt7-qfW1FJoHDEFKFxhfMpHQQoETa-jTPhCxOD2MzYM8A-9kKc8tu9r-crTAl1PI42kPnMd283phixd5G5Tv8gSaGdnq-45ka0iRuC7TItUdDiMNb_2YzB4ZLGLNmaIKQJSGqCHEcQuRVyxJtTZwrXaMMOhDqJaWUvUQWF5C7g5O5mOVTkNKw6ujzhqcWa4N3NE-HwcbVW_9st4s1c_ng-DlwLTptaeM5j-LOeZMX1zcVlwYMi5ZkYYY6FHHjYI4nBWDtqhvf-64QaTv8exIjk8PcxHOwhfLTWiHPLk14af7U_pCzkP87WQCBgNfvt3WILQ5DQ', 'p': '75eNHkWaYQMgzVfFwif5uftSxqOhFU6VkxNKdqoRuFxJuVTO-M-vbQc3BwPxms2xrpizU6zGcoPGPvccDi0G040wZh34pWDVABMgGMKXKmeTwj8FuM1DzOVq8DKHmdrhk1gaQbPAP8JVOVYK7uh_lG5wmz3X-En1McMk-E8g8Ic', 'q': '0Sny6DLNtDP1_B9qiyCaMtRqPSAUZ1ohCZRlBT6-IGRR31Kt5S2JcVNDnF5w4dunlDY4nhIBZ0v0VyzWKgDXj6qrFY1pm1iE29gW227YsVRWQU8xWGpBwEu8nxNMr0u0zfe0QEGWU4RvNAsZPRa31HU87Vm7I3NSZ34DZsCZJoc', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}
TA_JWK_PUBLIC = {'kty': 'RSA', 'n': 'w8H80eT2zrs2XQ-SApZG9TkuXDuIxANfCVHt4fFqNnOEZaCNWqlTQIo0JiSBE-QmzZ09TYP1BJpESuQf_PUeLRVPfYHsBVk5OYvhT27_nYlV7_1LsFGLxxsIa-hswMMzvW-1_huKLy6Fp0WP0ouUJAHsF_eYVtO1ApRhvlIVd5azM4k7t8Lh8lkCSdF1SfGHfXnXJRb-XensZ0cFSfe2Koq9mD7jpGLXlPpXxj8Ow0g7KYT5kVtWE5ULmNmO7BIN1Hx4HpggbbEGgC9FyjKw4GfFb-csnB-icBPf_60HomjrkFFt6vTjrcqQaHOj-sEjP36N8rMSBiMmiMSPnsHhMQ', 'e': 'AQAB', 'kid': 'HIvo33-Km7n03ZqKDJfWVnlFudsW28YhQZx5eaXtAKA'}

ta_conf_data_as_json = dict(
    sub=TA_SUB,
    iss=TA_SUB,
    metadata=FA_METADATA,
    jwks ={
        "keys": [TA_JWK_PUBLIC]
    },
    constraints=FA_CONSTRAINTS,
    is_active=1,
    trust_marks_issuers=TM_ISSUERS,
)
