from django.views.generic import TemplateView
from django.db.models import Count, F, ExpressionWrapper, fields, Sum
from django.utils.timezone import now, timedelta
from datetime import date
from web_project import TemplateLayout
from apps.volontaires.models import ContactForm
import json

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Disponibilités et leurs traductions
        availability_fields = [
            'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
            'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
            'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
            'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
            'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
            'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
            'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening'
        ]

        availability_translations = {
            'monday_all_day': 'Lundi - Toute la journée',
            'monday_morning': 'Lundi - Matin',
            'monday_afternoon': 'Lundi - Après-midi',
            'monday_evening': 'Lundi - Soir',
            'tuesday_all_day': 'Mardi - Toute la journée',
            'tuesday_morning': 'Mardi - Matin',
            'tuesday_afternoon': 'Mardi - Après-midi',
            'tuesday_evening': 'Mardi - Soir',
            'wednesday_all_day': 'Mercredi - Toute la journée',
            'wednesday_morning': 'Mercredi - Matin',
            'wednesday_afternoon': 'Mercredi - Après-midi',
            'wednesday_evening': 'Mercredi - Soir',
            'thursday_all_day': 'Jeudi - Toute la journée',
            'thursday_morning': 'Jeudi - Matin',
            'thursday_afternoon': 'Jeudi - Après-midi',
            'thursday_evening': 'Jeudi - Soir',
            'friday_all_day': 'Vendredi - Toute la journée',
            'friday_morning': 'Vendredi - Matin',
            'friday_afternoon': 'Vendredi - Après-midi',
            'friday_evening': 'Vendredi - Soir',
            'saturday_all_day': 'Samedi - Toute la journée',
            'saturday_morning': 'Samedi - Matin',
            'saturday_afternoon': 'Samedi - Après-midi',
            'saturday_evening': 'Samedi - Soir',
            'sunday_all_day': 'Dimanche - Toute la journée',
            'sunday_morning': 'Dimanche - Matin',
            'sunday_afternoon': 'Dimanche - Après-midi',
            'sunday_evening': 'Dimanche - Soir'
        }

        # Préparer les options de disponibilité pour le template
        context['availability_options'] = [
            {'field': field, 'translation': availability_translations[field]}
            for field in availability_fields
        ]

        # Dates par défaut: début et fin du mois en cours
        today = now().date()
        default_start_date = today.replace(day=1)
        default_end_date = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Récupération des dates depuis les paramètres GET ou utilisation des valeurs par défaut
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else default_start_date
        end_date = date.fromisoformat(end_date_str) if end_date_str else default_end_date

        # Convert dates to string in ISO format for use in the template
        context['start_date'] = start_date.isoformat()
        context['end_date'] = end_date.isoformat()

        # Filtrage des contacts
        contacts = ContactForm.objects.filter(start_date__gte=start_date, end_date__lte=end_date)

        availability = self.request.GET.get('availability')
        if availability:
            contacts = contacts.filter(**{availability: True})

        # Statistiques mises à jour
        context['total_contacts'] = contacts.count()

        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        context['new_contacts_last_week'] = contacts.filter(start_date__gte=last_week).count()
        context['new_contacts_last_month'] = contacts.filter(start_date__gte=last_month).count()

        # Contacts par disponibilité pour une fenêtre de 14 jours
        start_date_window = now()
        end_date_window = start_date_window + timedelta(days=13)
        dates = [start_date_window + timedelta(days=i) for i in range(14)]
        contacts_by_dates_slots = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts.filter(**{f'{date.strftime("%A").lower()}_{slot}': True}).count()
                for slot in ['all_day', 'morning', 'afternoon', 'evening']
            }
            for date in dates
        }
        context['contacts_by_dates_slots'] = json.dumps(contacts_by_dates_slots)
        context['dates'] = [date.strftime('%Y-%m-%d') for date in dates]

        # Meilleurs contributeurs
        date_diff = ExpressionWrapper(F('end_date') - F('start_date'), output_field=fields.DurationField())
        top_contributors = contacts.values('first_name', 'last_name').annotate(total_days=Sum(date_diff)).order_by('-total_days')[:5]
        context['top_contributors'] = list(top_contributors)

        return context
