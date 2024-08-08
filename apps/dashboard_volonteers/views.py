from django.views.generic import TemplateView
from django.db.models import Count, F, ExpressionWrapper, fields, Sum
from django.utils.timezone import now, timedelta
from web_project import TemplateLayout
from apps.volontaires.models import ContactForm
import json

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Extraction des disponibilités uniques depuis les champs
        availability_fields = [
            'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
            'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
            'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
            'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
            'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
            'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
            'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening'
        ]

        # Traductions des disponibilités en français
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

        # Filtrage des contacts en fonction des critères de l'utilisateur
        today = now().date()
        start_date = today.replace(day=1)
        end_date = today.replace(day=1) + timedelta(days=31)
        end_date = end_date.replace(day=1) - timedelta(days=1)
        availability = self.request.GET.get('availability')

        contacts = ContactForm.objects.all()

        if start_date:
            contacts = contacts.filter(start_date__gte=start_date)
        if end_date:
            contacts = contacts.filter(end_date__lte=end_date)
        if availability:
            contacts = contacts.filter(**{availability: True})

        # Total contacts
        context['total_contacts'] = contacts.count()

        # New contacts in the last week and last month
        last_week = now() - timedelta(days=7)
        last_month = now() - timedelta(days=30)
        context['new_contacts_last_week'] = contacts.filter(start_date__gte=last_week).count()
        context['new_contacts_last_month'] = contacts.filter(start_date__gte=last_month).count()

        # Contacts by start date
        contacts_by_start_date = contacts.values('start_date').annotate(count=Count('id')).order_by('start_date')
        context['contacts_by_start_date'] = list(contacts_by_start_date)

        # Contacts by duration
        date_diff = ExpressionWrapper(F('end_date') - F('start_date'), output_field=fields.DurationField())
        contacts_by_duration = contacts.values('first_name', 'last_name').annotate(duration=date_diff).order_by('duration')
        context['contacts_by_duration'] = list(contacts_by_duration)

        # Contacts by availability for a 14-day window
        start_date = now()
        end_date = start_date + timedelta(days=13)  # 14 days range
        dates = [start_date + timedelta(days=i) for i in range(14)]
        contacts_by_dates_slots = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts.filter(**{f'{date.strftime("%A").lower()}_{slot}': True}).count()
                for slot in ['all_day', 'morning', 'afternoon', 'evening']
            }
            for date in dates
        }
        context['contacts_by_dates_slots'] = json.dumps(contacts_by_dates_slots)
        context['dates'] = [date.strftime('%Y-%m-%d') for date in dates]

        # Days without contact
        days_without_contact = [
            date.strftime('%Y-%m-%d') for date in dates
            if all(contacts_by_dates_slots[date.strftime('%Y-%m-%d')][slot] == 0 for slot in ['all_day', 'morning', 'afternoon', 'evening'])
        ]
        context['days_without_contact'] = len(days_without_contact)
        context['days_without_contact_list'] = days_without_contact

        # Top contributors
        top_contributors = (contacts
                            .values('first_name', 'last_name')
                            .annotate(total_days=Sum(date_diff))
                            .order_by('-total_days')[:5])
        context['top_contributors'] = list(top_contributors)

        return context
