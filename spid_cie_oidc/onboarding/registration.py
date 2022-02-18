from django.forms import ModelForm
from .models import EntityModel


class RegistrationForm(ModelForm):

    class Meta:
        model = EntityModel
        fields = '__all__'
        
