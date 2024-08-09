from django.views.generic import TemplateView
from django.utils.dateparse import parse_date
from datetime import date, timedelta
from apps.volontaires.models import ContactForm
from web_project import TemplateLayout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class TableView(TemplateView):
    template_name = 'contact_form_list.html'
    paginate_by = 10  # Number of items per page

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get today's date
        today = date.today()
        default_start_date = today.replace(day=1)
        default_end_date = (default_start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Get the filter parameters or use default dates
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        availability = self.request.GET.getlist('availability')

        start_date = parse_date(start_date) if start_date else default_start_date
        end_date = parse_date(end_date) if end_date else default_end_date

        # Build the query
        filters = {}
        if start_date:
            filters['start_date__gte'] = start_date
        if end_date:
            filters['end_date__lte'] = end_date
        for day in availability:
            if day in ContactForm._meta.get_fields():
                filters[day] = True

        # Query the database with the filtering and sorting parameters
        sort_by = self.request.GET.get('sort', 'first_name')
        order = self.request.GET.get('order', 'asc')
        if order == 'desc':
            sort_by = '-' + sort_by

        contact_list = ContactForm.objects.filter(**filters).order_by(sort_by)

        # Paginate the contacts
        paginator = Paginator(contact_list, self.paginate_by)
        page = self.request.GET.get('page', 1)
        
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)

        # Add the contacts to the context
        context['contacts'] = contacts
        context['total_contacts'] = contact_list.count()

        # Add the current sort parameters to the context
        context['current_sort'] = sort_by.lstrip('-')
        context['current_order'] = order

        # Add filter parameters to the context
        context['current_start_date'] = start_date.isoformat()
        context['current_end_date'] = end_date.isoformat()
        context['current_availability'] = availability
        
        return context
