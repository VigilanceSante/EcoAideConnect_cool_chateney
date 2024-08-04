from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.form_layouts.models import ContactForm

class TableView(TemplateView):
    template_name = 'contact_form_list.html'

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['contacts'] = ContactForm.objects.all()
        return context
