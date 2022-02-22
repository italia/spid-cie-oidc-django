import imp
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _

from .forms import OnboardingRegistrationForm
from .models import OnBoardingRegistration


def onboarding_landing(request):
    return render(request, "onboarding_landing.html")


def onboarding_registration(request):
    form = OnboardingRegistrationForm()
    context = {'form': form}
    if request.method == 'POST':
        form = OnboardingRegistrationForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
        else:
            form_dict = {**form.cleaned_data}
            OnBoardingRegistration.objects.create(**form_dict)
            messages.success(request, _('Registration successfully'))
            return redirect('oidc_onboarding_landing')
    return render(request, 'onboarding_registration.html', context)


def onboarding_entities (request):
    entity_list = OnBoardingRegistration.objects.all()
    p = Paginator(entity_list, 10)
    page = request.GET.get('page')
    entities = p.get_page(page)
    return render(
        request,
        "onboarding_entities.html",
        {"entity_list": entity_list, "entities": entities},
    )
