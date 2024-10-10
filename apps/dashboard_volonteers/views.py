from django.views.generic import TemplateView
from django.db.models import Count, F, ExpressionWrapper, fields, Sum, Q
from django.utils.timezone import now, timedelta
from datetime import date
from web_project import TemplateLayout
from apps.volonteers.models import ContactForm
import json

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Define availability fields
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        slots = ['all_day', 'morning', 'afternoon', 'evening']
        availability_fields = [f"{day}_{slot}" for day in days_of_week for slot in slots]

        # Prepare availability translations
        availability_translations = {
            f"{day}_{slot}": f"{day.capitalize()} - {slot.replace('_', ' ').title()}"
            for day in days_of_week
            for slot in slots
        }

        # Prepare availability options for the template
        context['availability_options'] = [
            {'field': field, 'translation': availability_translations[field]}
            for field in availability_fields
        ]

        # Default dates: start and end of the current month
        today = now().date()
        default_start_date = today.replace(day=1)
        default_end_date = (default_start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Retrieve dates from GET parameters or use default values
        start_date = self.request.GET.get('start_date', default_start_date.isoformat())
        end_date = self.request.GET.get('end_date', default_end_date.isoformat())

        # Convert strings to date objects
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        context['start_date'] = start_date.isoformat()
        context['end_date'] = end_date.isoformat()

        # Filter contacts: only volunteers
        contacts = ContactForm.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, is_volunteer=True
        )

        availability = self.request.GET.get('availability')
        if availability:
            contacts = contacts.filter(**{availability: True})

        # KPI Calculations

        # 1. Weekend availability
        weekend_contacts = contacts.filter(
            Q(saturday_all_day=True) | Q(saturday_morning=True) | Q(saturday_afternoon=True) | Q(saturday_evening=True) |
            Q(sunday_all_day=True) | Q(sunday_morning=True) | Q(sunday_afternoon=True) | Q(sunday_evening=True)
        )
        context['weekend_contacts_count'] = weekend_contacts.count()

        # 2. Re-registered volunteers
        all_contacts = ContactForm.objects.filter(is_volunteer=True)
        re_registered_contacts = all_contacts.values('first_name', 'last_name').annotate(
            participation_count=Count('id')
        ).filter(participation_count__gt=1)

        context['re_registered_contacts_count'] = re_registered_contacts.count()

        # 3. Re-registration percentage
        distinct_volunteers = all_contacts.values('first_name', 'last_name').distinct().count()
        re_registration_percentage = (
            (re_registered_contacts.count() / distinct_volunteers) * 100 if distinct_volunteers > 0 else 0
        )
        context['re_registration_percentage'] = round(re_registration_percentage, 2)

        # 4. Total active volunteers
        context['total_active_volunteers'] = contacts.values('first_name', 'last_name').distinct().count()

        # 5. Contacts by availability for a 14-day window
        start_date_window = today
        dates_window = [start_date_window + timedelta(days=i) for i in range(14)]

        contacts_by_dates_slots = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts.filter(**{f"{date.strftime('%A').lower()}_{slot}": True}).count()
                for slot in slots
            }
            for date in dates_window
        }
        context['contacts_by_dates_slots'] = json.dumps(contacts_by_dates_slots)
        context['dates'] = [date.strftime('%Y-%m-%d') for date in dates_window]

        # 6. Availability trend for the last 14 days
        availability_trend = [
            contacts.filter(start_date__gte=(today - timedelta(days=days))).count() for days in range(14)
        ]
        context['availability_trend'] = json.dumps(availability_trend)

        # 7. Weekday vs Weekend contacts
        weekday_contacts = contacts.filter(
            Q(monday_all_day=True) | Q(monday_morning=True) | Q(monday_afternoon=True) | Q(monday_evening=True) |
            Q(tuesday_all_day=True) | Q(tuesday_morning=True) | Q(tuesday_afternoon=True) | Q(tuesday_evening=True) |
            Q(wednesday_all_day=True) | Q(wednesday_morning=True) | Q(wednesday_afternoon=True) | Q(wednesday_evening=True) |
            Q(thursday_all_day=True) | Q(thursday_morning=True) | Q(thursday_afternoon=True) | Q(thursday_evening=True) |
            Q(friday_all_day=True) | Q(friday_morning=True) | Q(friday_afternoon=True) | Q(friday_evening=True)
        )
        context['weekday_count'] = weekday_contacts.count()
        context['weekend_count'] = weekend_contacts.count()

        # 8. Top contributors
        date_diff = ExpressionWrapper(F('end_date') - F('start_date'), output_field=fields.DurationField())
        top_contributors = (
            contacts
            .values('first_name', 'last_name')
            .annotate(total_days=Sum(date_diff))
            .order_by('-total_days')[:5]
        )
        context['top_contributors'] = list(top_contributors)

        return context