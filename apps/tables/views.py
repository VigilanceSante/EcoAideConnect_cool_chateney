from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.volontaires.models import ContactForm

class TableView(TemplateView):
    template_name = 'contact_form_list.html'

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the sorting parameters from the request
        sort_by = self.request.GET.get('sort', 'first_name')
        order = self.request.GET.get('order', 'asc')

        # Determine the order (ascending or descending)
        if order == 'desc':
            sort_by = '-' + sort_by

        # Query the database with the sorting parameters
        context['contacts'] = ContactForm.objects.all().order_by(sort_by)
        
        # Add the current sort parameters to the context
        context['current_sort'] = self.request.GET.get('sort', 'first_name')
        context['current_order'] = self.request.GET.get('order', 'asc')
        
        return context
