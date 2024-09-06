from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import JsonResponse
import requests
from .forms import ContactFormForm
from web_project import TemplateLayout

class FormLayoutsView(TemplateView):
    template_name = 'contact_form.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = ContactFormForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactFormForm(request.POST)
        if form.is_valid():
            form.save()
            context = self.get_context_data(**kwargs)
            context['form'] = ContactFormForm()  # Réinitialiser le formulaire
            context['success_message'] = 'Votre formulaire a été soumis avec succès.'
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
        return self.render_to_response(context)

def address_autocomplete(request):
    query = request.GET.get('q', '')
    response = requests.get(f'https://api-adresse.data.gouv.fr/search/?q={query}=&postcode=92290')
    return JsonResponse(response.json())
