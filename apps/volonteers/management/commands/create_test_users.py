import requests
from django.core.management.base import BaseCommand
from apps.volonteers.models import ContactForm
from faker import Faker
import random
from datetime import timedelta, date
import unidecode

class Command(BaseCommand):
    help = 'Create test users with submissions across different months, ensuring specific rules for availability'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        def generate_phone_number():
            # Generate a French mobile number starting with 06 or 07
            return f"06{random.randint(10000000, 99999999)}"

        def fetch_real_address():
            # Make the API call to get real addresses from Châtenay-Malabry
            response = requests.get("https://api-adresse.data.gouv.fr/search/?q=Châtenay-Malabry&postcode=92290&limit=100")
            data = response.json()

            # Generate a random street number between 1 and 10
            street_number = random.randint(1, 10)

            if data['features']:
                # Randomly select an address from the API data
                selected_address = random.choice(data['features'])
                # Prepend the random street number to the selected address
                return f"{street_number} {selected_address['properties']['label']}"
            else:
                raise Exception("No addresses found in the API response")

        def get_day_of_week(date_obj):
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            return days[date_obj.weekday()]

        def create_submission(first_name, last_name, email, start_date, end_date, weekend_only=False, weekday_only=False):
            # Initialize availability to False for all timeslots
            availability = {
                'monday_all_day': False, 'monday_morning': False, 'monday_afternoon': False, 'monday_evening': False,
                'tuesday_all_day': False, 'tuesday_morning': False, 'tuesday_afternoon': False, 'tuesday_evening': False,
                'wednesday_all_day': False, 'wednesday_morning': False, 'wednesday_afternoon': False, 'wednesday_evening': False,
                'thursday_all_day': False, 'thursday_morning': False, 'thursday_afternoon': False, 'thursday_evening': False,
                'friday_all_day': False, 'friday_morning': False, 'friday_afternoon': False, 'friday_evening': False,
                'saturday_all_day': False, 'saturday_morning': False, 'saturday_afternoon': False, 'saturday_evening': False,
                'sunday_all_day': False, 'sunday_morning': False, 'sunday_afternoon': False, 'sunday_evening': False,
            }

            current_date = start_date
            while current_date <= end_date:
                day_of_week = get_day_of_week(current_date)
                
                if weekend_only and day_of_week in ["saturday", "sunday"]:
                    # Randomly assign either full day or specific times for weekend availability
                    if fake.boolean():
                        availability[f"{day_of_week}_all_day"] = True
                    else:
                        availability[f"{day_of_week}_morning"] = fake.boolean()
                        availability[f"{day_of_week}_afternoon"] = fake.boolean()
                        availability[f"{day_of_week}_evening"] = fake.boolean()

                elif weekday_only and day_of_week in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                    # Assign availability for the entire day for weekdays
                    availability[f"{day_of_week}_all_day"] = True
                
                current_date += timedelta(days=1)

            # Create the ContactForm object with defined availability
            ContactForm.objects.create(
                first_name=first_name,
                last_name=last_name,
                start_date=start_date,
                end_date=end_date,
                email=email,
                phone=generate_phone_number(),
                address=fetch_real_address(),
                monday_all_day=availability['monday_all_day'],
                monday_morning=availability['monday_morning'],
                monday_afternoon=availability['monday_afternoon'],
                monday_evening=availability['monday_evening'],
                tuesday_all_day=availability['tuesday_all_day'],
                tuesday_morning=availability['tuesday_morning'],
                tuesday_afternoon=availability['tuesday_afternoon'],
                tuesday_evening=availability['tuesday_evening'],
                wednesday_all_day=availability['wednesday_all_day'],
                wednesday_morning=availability['wednesday_morning'],
                wednesday_afternoon=availability['wednesday_afternoon'],
                wednesday_evening=availability['wednesday_evening'],
                thursday_all_day=availability['thursday_all_day'],
                thursday_morning=availability['thursday_morning'],
                thursday_afternoon=availability['thursday_afternoon'],
                thursday_evening=availability['thursday_evening'],
                friday_all_day=availability['friday_all_day'],
                friday_morning=availability['friday_morning'],
                friday_afternoon=availability['friday_afternoon'],
                friday_evening=availability['friday_evening'],
                saturday_all_day=availability['saturday_all_day'],
                saturday_morning=availability['saturday_morning'],
                saturday_afternoon=availability['saturday_afternoon'],
                saturday_evening=availability['saturday_evening'],
                sunday_all_day=availability['sunday_all_day'],
                sunday_morning=availability['sunday_morning'],
                sunday_afternoon=availability['sunday_afternoon'],
                sunday_evening=availability['sunday_evening'],
                is_volunteer=True  # Always set to True
            )

        # Create users and submissions for each month
        def create_users_for_month(month, month_start, month_end, user_count, weekday_users=0, weekend_users=0):
            # Create users with weekday availability
            for _ in range(weekday_users):
                first_name = fake.first_name()
                last_name = fake.last_name()
                normalized_first_name = unidecode.unidecode(first_name.lower().replace(' ', '_'))
                normalized_last_name = unidecode.unidecode(last_name.lower().replace(' ', '_'))
                email = f"{normalized_first_name}.{normalized_last_name}@example.com"

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))
                create_submission(first_name, last_name, email, start_date, end_date, weekday_only=True)

            # Create users with weekend availability
            for _ in range(weekend_users):
                first_name = fake.first_name()
                last_name = fake.last_name()
                normalized_first_name = unidecode.unidecode(first_name.lower().replace(' ', '_'))
                normalized_last_name = unidecode.unidecode(last_name.lower().replace(' ', '_'))
                email = f"{normalized_first_name}.{normalized_last_name}@example.com"

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))
                create_submission(first_name, last_name, email, start_date, end_date, weekend_only=True)

        # Generate data for May
        create_users_for_month("May", date(2024, 5, 1), date(2024, 5, 31), user_count=2000)

        # Generate data for June, July, and August (randomly between 2500 and 3000 users)
        for month, start_date, end_date in [("June", date(2024, 6, 1), date(2024, 6, 30)),
                                            ("July", date(2024, 7, 1), date(2024, 7, 31)),
                                            ("August", date(2024, 8, 1), date(2024, 8, 31))]:
            create_users_for_month(month, start_date, end_date, user_count=random.randint(2500, 3000))

        # Generate data for September and October
        # 100 users are available during weekdays; the rest (900) are for weekends
        create_users_for_month("September", date(2024, 9, 1), date(2024, 9, 30), user_count=1000, weekday_users=100, weekend_users=900)
        create_users_for_month("October", date(2024, 10, 1), date(2024, 10, 31), user_count=1000, weekday_users=100, weekend_users=900)

        self.stdout.write(self.style.SUCCESS(f'Successfully created test users with multiple submissions'))