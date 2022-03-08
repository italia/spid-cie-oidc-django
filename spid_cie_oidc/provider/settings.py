from django.conf import settings
from spid_cie_oidc.entity.schemas.op_metadata import (
    OPMetadataCie,
    OPMetadataSpid
)
from spid_cie_oidc.onboarding.schemas.authn_requests import (
    AuthenticationRequestCie,
    AuthenticationRequestSpid
)
from spid_cie_oidc.onboarding.schemas.revocation_request import RevocationRequest
from spid_cie_oidc.onboarding.schemas.token_requests import TokenAuthnCodeRequest, TokenRefreshRequest

OIDCFED_PROVIDER_PROFILES = getattr(
    settings,
    "OIDCFED_PROVIDER_PROFILES",
    {
        "spid": {
            "authorization_request": AuthenticationRequestSpid,
            "op_metadata": OPMetadataSpid,
            "authorization_code": TokenAuthnCodeRequest,
            "refresh_token": TokenRefreshRequest,
            "revocation_request": RevocationRequest
        },
        "cie": {
            "authorization_request": AuthenticationRequestCie,
            "op_metadata": OPMetadataCie,
            "authorization_code": TokenAuthnCodeRequest,
            "refresh_token": TokenRefreshRequest,
            "revocation_request": RevocationRequest
        },
    },
)

OIDCFED_PROVIDER_SALT = getattr(settings, "OIDCFED_PROVIDER_SALT", "CHANGEME")


OIDCFED_DEFAULT_PROVIDER_PROFILE = getattr(settings, "OIDCFED_PROVIDER_PROFILE", "spid")

OIDCFED_PROVIDER_ATTRIBUTES_MAP = {
    # SPID
    "https://attributes.spid.gov.it/spidCode": (
        {
            "func": "spid_cie_oidc.provider.processors.spidCode",
            "kwargs": {"salt": "signiicusenza"},
        },
    ),
    "https://attributes.spid.gov.it/name": ("name", "given_name"),
    "https://attributes.spid.gov.it/familyName": ("family_name", "surname"),
    "https://attributes.spid.gov.it/placeOfBirth": ("place_of_birth",),
    "https://attributes.spid.gov.it/countyOfBirth": ("county_of_birth",),
    "https://attributes.spid.gov.it/dateOfBirth": ("date_of_birth", "birthdate"),
    "https://attributes.spid.gov.it/gender": ("gender",),
    "https://attributes.spid.gov.it/companyName": ("company_name",),
    "https://attributes.spid.gov.it/registeredOffice": ("registered_office",),
    "https://attributes.spid.gov.it/fiscalNumber": ("fiscal_number", "tin"),
    "https://attributes.spid.gov.it/ivaCode": ("iva_code",),
    "https://attributes.spid.gov.it/idCard": ("id_card",),
    "https://attributes.spid.gov.it/mobilePhone": (
        "mobile_phone",
        "phone",
        "telephone",
    ),
    "https://attributes.spid.gov.it/email": ("email",),
    "https://attributes.spid.gov.it/address": ("address",),
    "https://attributes.spid.gov.it/expirationDate": ("expiration_date",),
    "https://attributes.spid.gov.it/digitalAddress": ("digital_address",),
    # CIE
    "given_name": ("name", "given_name"),
    "family_name": ("family_name", "surname"),
    "email": ("email",),
    "fiscal_number": ("fiscal_number", "tin"),
    "email_verified": ("email",),
    "gender": ("gender",),
    "birthdate": ("date_of_birth",),
    "phone_number": ("mobile_phone", "phone", "telephone"),
    "phone_number_verified": ("mobile_phone", "phone", "telephone"),
    "address": ("address",),
    "place_of_birth": ("place_of_birth",),
    # "document_details":  ,
    # "e_delivery_service":  ,
    "physical_phone_number": ("mobile_phone", "phone", "telephone"),
}
