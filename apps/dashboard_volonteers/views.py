from django.views.generic import TemplateView
from django.db.models import Count, F, ExpressionWrapper, fields, Sum, Q
from django.utils.timezone import now, timedelta
from datetime import date
from apps.db_users.models import ContactForm  # Assurez-vous que le chemin du modèle est correct
import json
from web_project import TemplateLayout


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Define availability fields for days and slots
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        slots = ['all_day', 'morning', 'afternoon', 'evening']

        # Default date range: Current month
        today = now().date()
        default_start_date = today.replace(day=1)
        default_end_date = (default_start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Get filter dates from GET params or default values
        start_date = self.request.GET.get('start_date', default_start_date.isoformat())
        end_date = self.request.GET.get('end_date', default_end_date.isoformat())
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        context['start_date'] = start_date.isoformat()
        context['end_date'] = end_date.isoformat()

        ### Volunteers ###
        contacts_volunteers = ContactForm.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, is_volunteer=True
        )

        ### Seekers (is_volunteer=False) ###
        contacts_seekers = ContactForm.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, is_volunteer=False
        )

        # 1. Total active volunteers
        context['total_active_volunteers'] = contacts_volunteers.values('first_name', 'last_name').distinct().count()

        # 2. Total seekers (non-volunteers)
        context['total_seekers'] = contacts_seekers.values('first_name', 'last_name').distinct().count()

        ### KPI Calculations for Volunteers ###

        # Weekend availability (Volunteers)
        weekend_contacts_volunteers = contacts_volunteers.filter(
            Q(saturday_all_day=True) | Q(saturday_morning=True) | Q(saturday_afternoon=True) | Q(saturday_evening=True) |
            Q(sunday_all_day=True) | Q(sunday_morning=True) | Q(sunday_afternoon=True) | Q(sunday_evening=True)
        )
        context['weekend_contacts_count'] = weekend_contacts_volunteers.count()

        # 3. Re-registered volunteers
        re_registered_volunteers = contacts_volunteers.values('first_name', 'last_name').annotate(
            participation_count=Count('id')
        ).filter(participation_count__gt=1)
        context['re_registered_contacts_count'] = re_registered_volunteers.count()

        # Re-registration percentage
        distinct_volunteers = contacts_volunteers.values('first_name', 'last_name').distinct().count()
        re_registration_percentage = (re_registered_volunteers.count() / distinct_volunteers * 100) if distinct_volunteers > 0 else 0
        context['re_registration_percentage'] = round(re_registration_percentage, 2)

        ### KPI Calculations for Seekers ###

        # Weekend availability (Seekers)
        weekend_contacts_seekers = contacts_seekers.filter(
            Q(saturday_all_day=True) | Q(saturday_morning=True) | Q(saturday_afternoon=True) | Q(saturday_evening=True) |
            Q(sunday_all_day=True) | Q(sunday_morning=True) | Q(sunday_afternoon=True) | Q(sunday_evening=True)
        )
        context['weekend_seekers_count'] = weekend_contacts_seekers.count()

        # Re-registered seekers (participating more than once)
        re_registered_seekers = contacts_seekers.values('first_name', 'last_name').annotate(
            participation_count=Count('id')
        ).filter(participation_count__gt=1)
        context['re_registered_seekers_count'] = re_registered_seekers.count()

        # 4. Contacts by availability for the next 14 days (Volunteers)
        dates_window = [today + timedelta(days=i) for i in range(14)]
        contacts_by_dates_slots_volunteers = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts_volunteers.filter(**{f"{date.strftime('%A').lower()}_{slot}": True}).count()
                for slot in slots
            }
            for date in dates_window
        }
        context['contacts_by_dates_slots'] = json.dumps(contacts_by_dates_slots_volunteers)
        context['dates'] = [date.strftime('%Y-%m-%d') for date in dates_window]

        # 5. Availability trend for the last 14 days (Volunteers)
        availability_trend = [
            contacts_volunteers.filter(start_date__gte=(today - timedelta(days=days))).count() for days in range(14)
        ]
        context['availability_trend'] = json.dumps(availability_trend)

        # Weekday vs Weekend for Volunteers
        weekday_contacts_volunteers = contacts_volunteers.filter(
            Q(monday_all_day=True) | Q(tuesday_all_day=True) | Q(wednesday_all_day=True) | Q(thursday_all_day=True) |
            Q(friday_all_day=True)
        )
        context['weekday_volunteers_count'] = weekday_contacts_volunteers.count()
        context['weekend_volunteers_count'] = weekend_contacts_volunteers.count()

        # Weekday vs Weekend for Seekers
        weekday_contacts_seekers = contacts_seekers.filter(
            Q(monday_all_day=True) | Q(tuesday_all_day=True) | Q(wednesday_all_day=True) | Q(thursday_all_day=True) |
            Q(friday_all_day=True)
        )
        context['weekday_seekers_count'] = weekday_contacts_seekers.count()
        context['weekend_seekers_count'] = weekend_contacts_seekers.count()

        # Top contributors (based on total days of availability)
        date_diff = ExpressionWrapper(F('end_date') - F('start_date'), output_field=fields.DurationField())
        top_contributors = contacts_volunteers.values('first_name', 'last_name').annotate(
            total_days=Sum(date_diff)
        ).order_by('-total_days')[:5]
        context['top_contributors'] = list(top_contributors)

        return context