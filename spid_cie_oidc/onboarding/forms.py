from django import forms


class OnboardingRegistrationForm(forms.Form):
    
    organization_name = forms.CharField(
        label= "organization Name",
        max_length=100,
    )

    url_entity = forms.URLField(
        initial='https://',
        label="url of the entity"
    )

    url_available = forms.URLField(
        initial='http://',
        label="url of the page where the SPID/CIE button is available"
    )

    public_jwks_of_entities = forms.CharField(
        label="public jwks of the entities"
    )
