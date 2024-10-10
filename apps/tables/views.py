from django.views.generic import TemplateView
from django.utils.dateparse import parse_date
from datetime import date, timedelta
from apps.volonteers.models import ContactForm
from web_project import TemplateLayout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class TableView(TemplateView):
    template_name = 'contact_form_list.html'
    paginate_by = 10  # Number of items per page

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get today's date
        today = date.today()
        default_start_date = today.replace(day=1)
        default_end_date = (default_start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Get the filter parameters or use default dates
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        start_date = parse_date(start_date) if start_date else default_start_date
        end_date = parse_date(end_date) if end_date else default_end_date

        # Determine availability options based on selected dates
        availability_options = []
        if start_date and end_date:
            days_of_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            time_slots = ["toute_la_journee", "matin", "apres_midi", "soir"]

            # Generate availability options based on the selected dates
            for day in days_of_week:
                for slot in time_slots:
                    availability_options.append({
                        'value': f"{day}_{slot}",
                        'label': f"{day.capitalize()} {slot.replace('_', ' ')}"
                    })

        # Additional context
        context['availability_options'] = availability_options

        # Build filters and query contacts
        filters = {}
        # Add other filters logic here...

        contact_list = ContactForm.objects.filter(**filters).order_by('first_name')  # Example

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
        return context