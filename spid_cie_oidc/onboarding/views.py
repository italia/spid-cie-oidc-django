from django.shortcuts import render

from .forms import OnboardingRegistrationForm


def onboarding_landing (request):
    return render(request, 'onboarding_landing.html')


def onboarding_registration (request):
    form = OnboardingRegistrationForm()

    context ={'form': form}
    return render(request, 'onboarding_registration.html', context)


def onboarding_entities (request):
    entity_list = [
        {"name_organization": "name organization 1", "url_entity": "https://organization1.it"}, 
        {"name_organization": "name organization 2", "url_entity": "https://organization2.it"},
        {"name_organization": "name organization 2", "url_entity": "https://organization2.it"}
    ]
    p = Paginator(entity_list, 1)
    page = request.GET.get('page')
    entities = p.get_page(page)
    return render(request, 'onboarding_entities.html', 
        {'entity_list': entity_list, 'entities': entities })
