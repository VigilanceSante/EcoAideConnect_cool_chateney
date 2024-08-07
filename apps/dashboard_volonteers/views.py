from django.views.generic import TemplateView
from django.db.models import Count
from web_project import TemplateLayout
from apps.volontaires.models import ContactForm

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Ajouter des statistiques et des données au tableau de bord
        context['total_contacts'] = ContactForm.objects.count()

        # Contacts par date de début
        contacts_by_start_date = ContactForm.objects.values('start_date').annotate(count=Count('id')).order_by('start_date')
        context['contacts_by_start_date'] = list(contacts_by_start_date)

        # Contacts par date de fin
        contacts_by_end_date = ContactForm.objects.values('end_date').annotate(count=Count('id')).order_by('end_date')
        context['contacts_by_end_date'] = list(contacts_by_end_date)

        # Contacts par disponibilité
        availability_fields = [
            'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
            'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
            'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
            'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
            'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
            'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
            'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening',
        ]

        availability_counts = {}
        for field in availability_fields:
            availability_counts[field] = ContactForm.objects.filter(**{field: True}).count()

        context['availability_counts'] = availability_counts

        # Meilleurs contributeurs
        top_contributors = ContactForm.objects.values('first_name', 'last_name').annotate(contributions=Count('id')).order_by('-contributions')[:5]
        context['top_contributors'] = top_contributors

        return context
