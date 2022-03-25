from .models import OnBoardingRegistration
from django.core.exceptions import ValidationError


def unique_entity_url(value): # pragma: no cover
    if OnBoardingRegistration.objects.filter(url_entity=value):
        raise ValidationError(f"{value} already onboarded")


def trust_anchor_validator(value): # pragma: no cover
    pass
    # raise ValidationError(f"{value} trust anchor not exist")
