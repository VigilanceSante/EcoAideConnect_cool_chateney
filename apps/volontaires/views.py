from django.views.generic import TemplateView
from django.shortcuts import redirect
from web_project import TemplateLayout
from .forms import ContactFormForm

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
            context['form'] = ContactFormForm()  # Reset the form
            context['success_message'] = 'Votre formulaire a été soumis avec succès.'
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
        return self.render_to_response(context)

