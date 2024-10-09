from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from apps.db_users.models import ContactForm
from web_project import TemplateLayout


class BuddiesDashboardView(TemplateView):
    template_name = 'twosome.html'
    
    def get_context_data(self, **kwargs):
        """Prépare les données pour le template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Récupérer les dates de filtrage et les filtres de disponibilité
        start_date = self.get_start_date()
        availability_filters = self.get_availability_filters()

        # Filtrer et paginer les buddies disponibles à partir de J+7
        filtered_buddies = self.filter_buddies_from_j7(start_date, availability_filters)
        buddy_pairs_page = self.paginate_buddy_pairs(filtered_buddies)

        # Mise à jour du contexte
        context.update({
            'buddy_pairs': buddy_pairs_page,
            'start_date': start_date,
        })
        return context

    def get_start_date(self):
        """Calculer et retourner la date de J+7."""
        today = datetime.today()
        j_plus_7 = today + timedelta(days=7)
        return j_plus_7.strftime('%Y-%m-%d')

    def get_availability_filters(self):
        """Obtenir les filtres de disponibilité depuis la requête."""
        return self.request.GET.getlist('availability')

    def filter_buddies_from_j7(self, start_date, availability_filters):
        """Filtrer les buddies disponibles à partir de J+7."""
        # Filtrer par start_date >= J+7
        buddies = ContactForm.objects.filter(submit_at__gte=start_date)

        # Appliquer les filtres de disponibilité, si disponibles
        if availability_filters:
            availability_query = self.build_availability_query(availability_filters)
            buddies = buddies.filter(availability_query)

        return self.get_buddy_pairs(buddies)

    def build_availability_query(self, availability_filters):
        """Construire la requête Q pour filtrer par disponibilité."""
        return Q(**{f"{availability}": True for availability in availability_filters})

    def get_buddy_pairs(self, buddies):
        """Retourner les paires de buddies avec leur disponibilité respective."""
        buddy_pairs = []
        for buddy in buddies:
            paired_buddy = ContactForm.objects.filter(id=buddy.buddy_id).first()
            if paired_buddy:
                buddy_pairs.append({
                    'person': buddy,
                    'buddy': paired_buddy,
                    'person_slots': self.get_availability_slots(buddy),
                    'buddy_slots': self.get_availability_slots(paired_buddy)
                })
        return buddy_pairs

    def get_availability_slots(self, buddy):
        """Retourner les créneaux de disponibilité d'un buddy sous forme lisible."""
        availability_fields = [
            'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
            'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
            'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
            'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
            'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
            'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
            'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening'
        ]

        slot_labels = {
            'monday_all_day': 'Lundi Toute la journée',
            'monday_morning': 'Lundi Matin',
            'monday_afternoon': 'Lundi Après-midi',
            'monday_evening': 'Lundi Soir',
            'tuesday_all_day': 'Mardi Toute la journée',
            'tuesday_morning': 'Mardi Matin',
            'tuesday_afternoon': 'Mardi Après-midi',
            'tuesday_evening': 'Mardi Soir',
            'wednesday_all_day': 'Mercredi Toute la journée',
            'wednesday_morning': 'Mercredi Matin',
            'wednesday_afternoon': 'Mercredi Après-midi',
            'wednesday_evening': 'Mercredi Soir',
            'thursday_all_day': 'Jeudi Toute la journée',
            'thursday_morning': 'Jeudi Matin',
            'thursday_afternoon': 'Jeudi Après-midi',
            'thursday_evening': 'Jeudi Soir',
            'friday_all_day': 'Vendredi Toute la journée',
            'friday_morning': 'Vendredi Matin',
            'friday_afternoon': 'Vendredi Après-midi',
            'friday_evening': 'Vendredi Soir',
            'saturday_all_day': 'Samedi Toute la journée',
            'saturday_morning': 'Samedi Matin',
            'saturday_afternoon': 'Samedi Après-midi',
            'saturday_evening': 'Samedi Soir',
            'sunday_all_day': 'Dimanche Toute la journée',
            'sunday_morning': 'Dimanche Matin',
            'sunday_afternoon': 'Dimanche Après-midi',
            'sunday_evening': 'Dimanche Soir',
        }

        # Filtrer et retourner les créneaux disponibles sous forme de liste
        return [slot_labels[field] for field in availability_fields if getattr(buddy, field, False)]

    def paginate_buddy_pairs(self, buddy_pairs):
        """Paginer la liste des paires de buddies (10 par page)."""
        paginator = Paginator(buddy_pairs, 10)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)