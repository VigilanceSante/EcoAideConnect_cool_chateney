from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .forms import ContactFormForm
from web_project import TemplateLayout

class FormLayoutsHelp(TemplateView):
    template_name = 'help.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Initialize the form with default values, if needed
        form = ContactFormForm(initial={'is_volunteer': False})  # Assuming is_volunteer is a form field
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = ContactFormForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=True)
            contact.is_volunteer = False  # Explicitly set is_volunteer to False
            contact.save()

            # Redirect to prevent form resubmission issues
            return HttpResponseRedirect(request.path_info)

        # If the form is not valid, render the form with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)
    
