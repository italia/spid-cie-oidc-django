from django import forms


class OnboardingRegistrationForm(forms.Form):
    
    organization_name = forms.CharField(
        label= "organization Name",
        error_messages={'required' : 'Enter your organization name'}
    )

    url_entity = forms.URLField(
        initial='https://',
        label="url of the entity",
        error_messages={'required' : 'Enter your url of the entity'}
    )

    url_available = forms.URLField(
        initial='http://',
        label="url of the page where the SPID/CIE button is available",
        error_messages={
            'required' : 'Enter the url of the page where the SPID/CIE button is available'}
    )

    public_jwks = forms.CharField(
        label="public jwks of the entities",
        error_messages={
            'required' : 'Enter the public jwks of the entities'}
    )
