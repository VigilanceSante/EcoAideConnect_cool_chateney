import requests
from django.core.management.base import BaseCommand
from apps.volonteers.models import ContactForm
from faker import Faker
import random
from datetime import timedelta, date
import unidecode

class Command(BaseCommand):
    help = 'Create test users with registrations across different months, ensuring specific rules for availability and re-registrations'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        previous_users = []

        def generate_phone_number():
            # Generate a French mobile number starting with 06
            return f"06{random.randint(10000000, 99999999)}"

        def fetch_real_address():
            # Make an API call to get real addresses from Châtenay-Malabry
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

        def create_submission(first_name, last_name, email, start_date, end_date, weekend_only=False, weekday_only=False, registration_date=None):
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

            # Set availability
            if weekend_only:
                for day in ['saturday', 'sunday']:
                    if fake.boolean():
                        availability[f"{day}_all_day"] = True
                    else:
                        availability[f"{day}_morning"] = fake.boolean()
                        availability[f"{day}_afternoon"] = fake.boolean()
                        availability[f"{day}_evening"] = fake.boolean()
            elif weekday_only:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    availability[f"{day}_all_day"] = True
            else:
                # Random availability
                for day in availability.keys():
                    availability[day] = fake.boolean()

            # Create the ContactForm object with defined availability and registration date
            submission = ContactForm.objects.create(
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
                is_volunteer=True,  # Always set to True
            )

            if registration_date:
                # Manually set the registration date if provided
                submission.created_at = registration_date
                submission.save()

        # Create users and submissions for each month
        def create_users_for_month(month, month_start, month_end, user_count, previous_users):
            # Calculate the number of users who re-register (60%)
            re_register_count = int(0.6 * len(previous_users))
            new_user_count = user_count - re_register_count

            # Create registration dates in multiple batches
            batch_dates = [
                month_start + timedelta(days=random.randint(0, 10)),
                month_start + timedelta(days=random.randint(11, 20)),
                month_start + timedelta(days=random.randint(21, 28)),
            ]

            # Select users who re-register
            re_register_users = random.sample(previous_users, re_register_count)

            # Re-register users
            for idx, user_info in enumerate(re_register_users):
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                email = user_info['email']

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))

                # Assign a registration date from the batches
                registration_date = batch_dates[idx % len(batch_dates)]

                create_submission(first_name, last_name, email, start_date, end_date, registration_date=registration_date)

            # Create new users
            new_users = []
            for idx in range(new_user_count):
                first_name = fake.first_name()
                last_name = fake.last_name()
                normalized_first_name = unidecode.unidecode(first_name.lower().replace(' ', '_'))
                normalized_last_name = unidecode.unidecode(last_name.lower().replace(' ', '_'))
                email = f"{normalized_first_name}.{normalized_last_name}@example.com"

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))

                # Assign a registration date from the batches
                registration_date = batch_dates[idx % len(batch_dates)]

                create_submission(first_name, last_name, email, start_date, end_date, registration_date=registration_date)

                new_users.append({'first_name': first_name, 'last_name': last_name, 'email': email})

            # Update the list of users for the next month
            return re_register_users + new_users

        # Specific handling from September onwards
        def create_users_for_month_september_onwards(month, month_start, month_end, user_count, previous_users):
            re_register_count = int(0.6 * len(previous_users))
            new_user_count = user_count - re_register_count

            batch_dates = [
                month_start + timedelta(days=random.randint(0, 10)),
                month_start + timedelta(days=random.randint(11, 20)),
                month_start + timedelta(days=random.randint(21, 28)),
            ]

            re_register_users = random.sample(previous_users, re_register_count)

            for idx, user_info in enumerate(re_register_users):
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                email = user_info['email']

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))

                # Approximately 10 people available during weekdays; the rest on weekends
                if idx < 10:
                    weekday_only = True
                    weekend_only = False
                else:
                    weekday_only = False
                    weekend_only = True

                registration_date = batch_dates[idx % len(batch_dates)]

                create_submission(
                    first_name, last_name, email, start_date, end_date,
                    weekend_only=weekend_only, weekday_only=weekday_only,
                    registration_date=registration_date
                )

            new_users = []
            for idx in range(new_user_count):
                first_name = fake.first_name()
                last_name = fake.last_name()
                normalized_first_name = unidecode.unidecode(first_name.lower().replace(' ', '_'))
                normalized_last_name = unidecode.unidecode(last_name.lower().replace(' ', '_'))
                email = f"{normalized_first_name}.{normalized_last_name}@example.com"

                start_date = fake.date_between_dates(date_start=month_start, date_end=month_end)
                end_date = start_date + timedelta(days=random.randint(2, 6))

                if idx < 10:
                    weekday_only = True
                    weekend_only = False
                else:
                    weekday_only = False
                    weekend_only = True

                registration_date = batch_dates[idx % len(batch_dates)]

                create_submission(
                    first_name, last_name, email, start_date, end_date,
                    weekend_only=weekend_only, weekday_only=weekday_only,
                    registration_date=registration_date
                )

                new_users.append({'first_name': first_name, 'last_name': last_name, 'email': email})

            return re_register_users + new_users

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
            if month_name in ["May", "June", "July", "August"]:
                previous_users = create_users_for_month(month_name, start_date, end_date, user_count, previous_users)
            else:
                previous_users = create_users_for_month_september_onwards(month_name, start_date, end_date, user_count, previous_users)

        self.stdout.write(self.style.SUCCESS('Successfully created test users with multiple batches of registration dates and re-registrations'))