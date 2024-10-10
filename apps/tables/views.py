from django.views.generic import TemplateView
from django.utils.dateparse import parse_date
from datetime import date, timedelta
from apps.volonteers.models import ContactForm
from web_project import TemplateLayout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class TableView(TemplateView):
    template_name = 'contact_form_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        contact_list = ContactForm.objects.all().order_by('first_name')  # Fetch all contacts
        
        # Paginate the contacts
        paginator = Paginator(contact_list, self.paginate_by)
        page = self.request.GET.get('page', 1)

        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)

        context['contacts'] = contacts
        context['total_contacts'] = contact_list.count()

        # Define availability options with corresponding model fields
        context['availability_slots'] = [
            {'field': 'thursday_all_day', 'label': 'Jeudi toute la journée'},
            {'field': 'thursday_morning', 'label': 'Jeudi matin'},
            {'field': 'thursday_afternoon', 'label': 'Jeudi après-midi'},
            {'field': 'thursday_evening', 'label': 'Jeudi soir'},
            # Add more slots for other days...
        ]

        return context