from django.views.generic import TemplateView
from django.db.models import Count, Q, F, Sum
from django.utils.timezone import now, timedelta
from datetime import date
from apps.db_users.models import ContactForm
import json
from web_project import TemplateLayout

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Default date range: Current month
        today = now().date()
        default_start_date = today.replace(day=1)
        default_end_date = (default_start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Get filter dates from GET params or default values
        start_date_str = self.request.GET.get('start_date', default_start_date.isoformat())
        end_date_str = self.request.GET.get('end_date', default_end_date.isoformat())
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        context['start_date'] = start_date.isoformat()
        context['end_date'] = end_date.isoformat()

        # Volunteers and Seekers Data
        contacts_volunteers = ContactForm.objects.filter(
            is_volunteer=True
        )
        contacts_seekers = ContactForm.objects.filter(
            is_volunteer=False
        )

        # Total active volunteers
        context['total_active_volunteers'] = contacts_volunteers.distinct().count()

        # Total seekers
        context['total_seekers'] = contacts_seekers.distinct().count()

        # Weekend volunteers
        weekend_contacts_volunteers = contacts_volunteers.filter(
            Q(saturday_all_day=True) | Q(saturday_morning=True) | Q(saturday_afternoon=True) | Q(saturday_evening=True) |
            Q(sunday_all_day=True) | Q(sunday_morning=True) | Q(sunday_afternoon=True) | Q(sunday_evening=True)
        )
        context['weekend_volunteers_count'] = weekend_contacts_volunteers.count()

        # Weekend seekers
        weekend_contacts_seekers = contacts_seekers.filter(
            Q(saturday_all_day=True) | Q(saturday_morning=True) | Q(saturday_afternoon=True) | Q(saturday_evening=True) |
            Q(sunday_all_day=True) | Q(sunday_morning=True) | Q(sunday_afternoon=True) | Q(sunday_evening=True)
        )
        context['weekend_seekers_count'] = weekend_contacts_seekers.count()

        # Re-registered volunteers
        re_registered_volunteers = contacts_volunteers.values('first_name', 'last_name').annotate(
            participation_count=Count('id')
        ).filter(participation_count__gt=1)
        context['re_registered_volunteers_count'] = re_registered_volunteers.count()

        # Count pairings created based on buddy_id
        pairings_created = ContactForm.objects.filter(
            buddy_id__isnull=False,  # Counting only those with a buddy_id
            start_date__gte=start_date,
            end_date__lte=end_date
        ).count()
        context['pairings_created_count'] = pairings_created

        # Prepare data for charts
        context['weekday_volunteers_count'] = contacts_volunteers.filter(
            Q(monday_all_day=True) | Q(tuesday_all_day=True) | Q(wednesday_all_day=True) | 
            Q(thursday_all_day=True) | Q(friday_all_day=True)
        ).count()

        context['weekday_seekers_count'] = contacts_seekers.filter(
            Q(monday_all_day=True) | Q(tuesday_all_day=True) | Q(wednesday_all_day=True) | 
            Q(thursday_all_day=True) | Q(friday_all_day=True)
        ).count()

        # Gather top contributors
        date_diff = F('end_date') - F('start_date')
        top_contributors = contacts_volunteers.values('first_name', 'last_name').annotate(
            total_days=Sum(date_diff)
        ).order_by('-total_days')[:5]
        context['top_contributors'] = list(top_contributors)

        # Prepare availability data for charts
        dates_window = [today + timedelta(days=i) for i in range(14)]
        contacts_by_dates_slots_volunteers = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts_volunteers.filter(**{f"{date.strftime('%A').lower()}_{slot}": True}).count()
                for slot in ['all_day', 'morning', 'afternoon', 'evening']
            }
            for date in dates_window
        }
        context['contacts_by_dates_slots_volunteers'] = json.dumps(contacts_by_dates_slots_volunteers)

        contacts_by_dates_slots_seekers = {
            date.strftime('%Y-%m-%d'): {
                slot: contacts_seekers.filter(**{f"{date.strftime('%A').lower()}_{slot}": True}).count()
                for slot in ['all_day', 'morning', 'afternoon', 'evening']
            }
            for date in dates_window
        }
        context['contacts_by_dates_slots_seekers'] = json.dumps(contacts_by_dates_slots_seekers)

        context['dates'] = [date.strftime('%Y-%m-%d') for date in dates_window]

        return context