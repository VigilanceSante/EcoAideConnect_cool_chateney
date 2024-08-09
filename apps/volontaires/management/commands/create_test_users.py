import requests
from django.core.management.base import BaseCommand
from apps.volontaires.models import ContactForm
from faker import Faker
import random
from datetime import timedelta
import unidecode

class Command(BaseCommand):
    help = 'Create test users'

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

        def get_day_of_week(date):
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            return days[date.weekday()]

        for _ in range(20):  # Adjust the range for the number of test users you want (here 20)
            first_name = fake.first_name()
            last_name = fake.last_name()
            normalized_first_name = unidecode.unidecode(first_name.lower().replace(' ', '_'))
            normalized_last_name = unidecode.unidecode(last_name.lower().replace(' ', '_'))
            email = f"{normalized_first_name}.{normalized_last_name}@example.com"
            start_date = fake.date_between(start_date='-30d', end_date='today')
            end_date = start_date + timedelta(days=random.randint(2, 6))  # Adjust the range for at least 2 days and at most 6 days
            
            # Initialize availability to False
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
                if fake.boolean():
                    # Mark the day as "all_day" available
                    availability[f"{day_of_week}_all_day"] = True
                else:
                    # Randomly mark the slots as available for the days between start_date and end_date
                    availability[f"{day_of_week}_morning"] = fake.boolean()
                    availability[f"{day_of_week}_afternoon"] = fake.boolean()
                    availability[f"{day_of_week}_evening"] = fake.boolean()
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
                monday_morning=availability['monday_morning'] if not availability['monday_all_day'] else False,
                monday_afternoon=availability['monday_afternoon'] if not availability['monday_all_day'] else False,
                monday_evening=availability['monday_evening'] if not availability['monday_all_day'] else False,
                tuesday_all_day=availability['tuesday_all_day'],
                tuesday_morning=availability['tuesday_morning'] if not availability['tuesday_all_day'] else False,
                tuesday_afternoon=availability['tuesday_afternoon'] if not availability['tuesday_all_day'] else False,
                tuesday_evening=availability['tuesday_evening'] if not availability['tuesday_all_day'] else False,
                wednesday_all_day=availability['wednesday_all_day'],
                wednesday_morning=availability['wednesday_morning'] if not availability['wednesday_all_day'] else False,
                wednesday_afternoon=availability['wednesday_afternoon'] if not availability['wednesday_all_day'] else False,
                wednesday_evening=availability['wednesday_evening'] if not availability['wednesday_all_day'] else False,
                thursday_all_day=availability['thursday_all_day'],
                thursday_morning=availability['thursday_morning'] if not availability['thursday_all_day'] else False,
                thursday_afternoon=availability['thursday_afternoon'] if not availability['thursday_all_day'] else False,
                thursday_evening=availability['thursday_evening'] if not availability['thursday_all_day'] else False,
                friday_all_day=availability['friday_all_day'],
                friday_morning=availability['friday_morning'] if not availability['friday_all_day'] else False,
                friday_afternoon=availability['friday_afternoon'] if not availability['friday_all_day'] else False,
                friday_evening=availability['friday_evening'] if not availability['friday_all_day'] else False,
                saturday_all_day=availability['saturday_all_day'],
                saturday_morning=availability['saturday_morning'] if not availability['saturday_all_day'] else False,
                saturday_afternoon=availability['saturday_afternoon'] if not availability['saturday_all_day'] else False,
                saturday_evening=availability['saturday_evening'] if not availability['saturday_all_day'] else False,
                sunday_all_day=availability['sunday_all_day'],
                sunday_morning=availability['sunday_morning'] if not availability['sunday_all_day'] else False,
                sunday_afternoon=availability['sunday_afternoon'] if not availability['sunday_all_day'] else False,
                sunday_evening=availability['sunday_evening'] if not availability['sunday_all_day'] else False,
            )
        self.stdout.write(self.style.SUCCESS('Successfully created 20 test users'))
