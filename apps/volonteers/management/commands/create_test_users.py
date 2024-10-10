from django.core.management.base import BaseCommand
from apps.db_users.models import ContactForm
from faker import Faker
import random
from datetime import timedelta, date, datetime
import unidecode
import requests
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Create test users with volunteers and seekers, ensuring each volunteer helps up to 2 seekers'

    def fetch_real_addresses(self):
        # Fetch real addresses from Châtenay-Malabry via API call
        response = requests.get("https://api-adresse.data.gouv.fr/search/?q=Châtenay-Malabry&postcode=92290&limit=100")
        data = response.json()
        if data['features']:
            return [f"{random.randint(1, 10)} {address['properties']['label']}" for address in data['features']]
        else:
            raise Exception("No addresses found in the API response")

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        previous_users = []
        volunteer_users = []

        # Ratio of volunteers to seekers (1 volunteer for every 2 seekers)
        volunteer_ratio = 1 / 3

        # Fetch real addresses once to avoid repetitive API calls
        addresses = self.fetch_real_addresses()

        def generate_phone_number():
            # Generate a French mobile number starting with 06
            return f"06{random.randint(10000000, 99999999)}"

        def validate_submission_dates(submit_at, start_date):
            # Ensure submit_at is no later than 2 days before start_date
            if submit_at > start_date - timedelta(days=2):
                raise ValidationError(f"Date of submission {submit_at} must be at least 2 days before start date {start_date}.")

        def create_availability_for_specific_day(selected_date):
            # Get the weekday from the selected_date (0 = Monday, 6 = Sunday)
            day_of_week = selected_date.weekday()

            # Map the day of the week to the corresponding string name
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            selected_day_name = day_names[day_of_week]

            # Initialize availability for all days as False
            availability = {f'{day}_{period}': False for day in day_names for period in ['all_day', 'morning', 'afternoon', 'evening']}

            # Set availability for the selected day
            availability[f'{selected_day_name}_all_day'] = True  # Mark the entire day as available

            return availability

        def create_users_in_bulk(users_data):
            # Use Django's bulk_create to insert multiple users at once for better performance
            ContactForm.objects.bulk_create([ContactForm(**data) for data in users_data])

        def generate_user_data(first_name, last_name, email, submit_at, start_date, end_date, is_volunteer=True):
            validate_submission_dates(submit_at, start_date)

            # Create availability only for the day corresponding to the start_date
            availability = create_availability_for_specific_day(start_date)

            return {
                'first_name': first_name,
                'last_name': last_name,
                'start_date': start_date,
                'end_date': end_date,
                'submit_at': submit_at,
                'email': email,
                'phone': generate_phone_number(),
                'address': random.choice(addresses),
                'monday_all_day': availability['monday_all_day'],
                'monday_morning': availability['monday_morning'],
                'monday_afternoon': availability['monday_afternoon'],
                'monday_evening': availability['monday_evening'],
                'tuesday_all_day': availability['tuesday_all_day'],
                'tuesday_morning': availability['tuesday_morning'],
                'tuesday_afternoon': availability['tuesday_afternoon'],
                'tuesday_evening': availability['tuesday_evening'],
                'wednesday_all_day': availability['wednesday_all_day'],
                'wednesday_morning': availability['wednesday_morning'],
                'wednesday_afternoon': availability['wednesday_afternoon'],
                'wednesday_evening': availability['wednesday_evening'],
                'thursday_all_day': availability['thursday_all_day'],
                'thursday_morning': availability['thursday_morning'],
                'thursday_afternoon': availability['thursday_afternoon'],
                'thursday_evening': availability['thursday_evening'],
                'friday_all_day': availability['friday_all_day'],
                'friday_morning': availability['friday_morning'],
                'friday_afternoon': availability['friday_afternoon'],
                'friday_evening': availability['friday_evening'],
                'saturday_all_day': availability['saturday_all_day'],
                'saturday_morning': availability['saturday_morning'],
                'saturday_afternoon': availability['saturday_afternoon'],
                'saturday_evening': availability['saturday_evening'],
                'sunday_all_day': availability['sunday_all_day'],
                'sunday_morning': availability['sunday_morning'],
                'sunday_afternoon': availability['sunday_afternoon'],
                'sunday_evening': availability['sunday_evening'],
                'is_volunteer': is_volunteer
            }

        def create_users_for_month(month, month_start, month_end, user_count, previous_users):
            re_register_count = int(0.6 * len(previous_users))
            new_user_count = user_count - re_register_count
            volunteer_count = int(volunteer_ratio * user_count)
            seeker_count = user_count - volunteer_count

            users_data = []

            # Re-register users
            re_register_users = random.sample(previous_users, re_register_count)
            for idx, user_info in enumerate(re_register_users):
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                email = user_info['email']
                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))
                submit_at = start_date - timedelta(days=random.randint(2, 4))
                users_data.append(generate_user_data(first_name, last_name, email, submit_at, start_date, end_date, is_volunteer=True))

            # Create new volunteers
            for idx in range(volunteer_count):
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{unidecode.unidecode(first_name.lower())}.{unidecode.unidecode(last_name.lower())}@example.com"
                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))
                submit_at = start_date - timedelta(days=random.randint(2, 4))
                users_data.append(generate_user_data(first_name, last_name, email, submit_at, start_date, end_date, is_volunteer=True))

            # Create new seekers
            for idx in range(seeker_count):
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{unidecode.unidecode(first_name.lower())}.{unidecode.unidecode(last_name.lower())}@example.com"
                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))
                submit_at = start_date - timedelta(days=random.randint(2, 4))
                users_data.append(generate_user_data(first_name, last_name, email, submit_at, start_date, end_date, is_volunteer=False))

            # Create users in bulk
            create_users_in_bulk(users_data)

            # Return updated users list for re-registration in the next months
            return re_register_users + [{'first_name': fake.first_name(), 'last_name': fake.last_name(), 'email': fake.email()} for _ in range(new_user_count)]

        # Simulate months from May to October
        months = [
            ("May", date(2024, 5, 1), date(2024, 5, 31), 2000),
            ("June", date(2024, 6, 1), date(2024, 6, 30), random.randint(2500, 3000)),
            ("July", date(2024, 7, 1), date(2024, 7, 31), random.randint(2500, 3000)),
            ("August", date(2024, 8, 1), date(2024, 8, 31), random.randint(2500, 3000)),
            ("September", date(2024, 9, 1), date(2024, 9, 30), 1000),
            ("October", date(2024, 10, 1), date(2024, 10, 31), 1000),
        ]

        for month_name, start_date, end_date, user_count in months:
            previous_users = create_users_for_month(month_name, start_date, end_date, user_count, previous_users)

        self.stdout.write(self.style.SUCCESS('Successfully created test users with volunteers and seekers.'))