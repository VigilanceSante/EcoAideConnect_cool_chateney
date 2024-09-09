from django.views.generic import TemplateView
from django.shortcuts import redirect
from .forms import HelpForm
from web_project import TemplateLayout

class FormLayoutsHelp(TemplateView):
    template_name = 'help.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = HelpForm()
        return context

    def post(self, request, *args, **kwargs):
        form = HelpForm(request.POST)
        if form.is_valid():
            form.save()  # This will save the form data to the database
            context = self.get_context_data(**kwargs)
            context['form'] = HelpForm()  # Reinitialize the form after successful submission
            context['success_message'] = 'Votre formulaire a été soumis avec succès.'
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form  # Re-render the form with errors
        return self.render_to_response(context)