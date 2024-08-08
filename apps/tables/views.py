from django.views.generic import TemplateView
from django.utils.dateparse import parse_date
from apps.volontaires.models import ContactForm
from web_project import TemplateLayout

class TableView(TemplateView):
    template_name = 'contact_form_list.html'

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the sorting parameters from the request
        sort_by = self.request.GET.get('sort', 'first_name')
        order = self.request.GET.get('order', 'asc')

        if order == 'desc':
            sort_by = '-' + sort_by

        # Filter parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        availability = self.request.GET.getlist('availability')

        # Build the query
        filters = {}
        if start_date:
            filters['start_date__gte'] = parse_date(start_date)
        if end_date:
            filters['end_date__lte'] = parse_date(end_date)
        for day in availability:
            if day in ContactForm._meta.get_fields():
                filters[day] = True

        # Query the database with the filtering and sorting parameters
        context['contacts'] = ContactForm.objects.filter(**filters).order_by(sort_by)
        
        # Add the current sort parameters to the context
        context['current_sort'] = self.request.GET.get('sort', 'first_name')
        context['current_order'] = self.request.GET.get('order', 'asc')

        # Add filter parameters to the context
        context['current_start_date'] = start_date
        context['current_end_date'] = end_date
        context['current_availability'] = availability
        
        return context
