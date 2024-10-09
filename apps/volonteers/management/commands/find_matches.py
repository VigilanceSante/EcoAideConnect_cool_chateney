from django.core.management.base import BaseCommand
from apps.volonteers.models import ContactForm

class Command(BaseCommand):
    help = 'Find matches between seekers and volunteers based on availability.'

    def handle(self, *args, **kwargs):
        matches = find_matches_with_info()

        for match in matches:
            seeker_info = match['seeker']
            volunteer_info = match['volunteer']
            self.stdout.write(
                f"Seeker {seeker_info['name']} (Phone: {seeker_info['phone']}, Email: {seeker_info['email']}, Address: {seeker_info['address']}) matched with "
                f"Volunteer {volunteer_info['name']} (Phone: {volunteer_info['phone']}, Email: {volunteer_info['email']}, Address: {volunteer_info['address']})"
            )

def find_matches_with_info():

    print('Find matches...')

    # Retrieve seekers and volunteers
    seekers = ContactForm.objects.filter(is_volunteer=False)
    volunteers = ContactForm.objects.filter(is_volunteer=True)

    matches = []

    # Compare availability and gather user information for matches
    for seeker in seekers:
        for volunteer in volunteers:
            if match_availability(seeker, volunteer):
                match_data = {
                    "seeker": {
                        "name": f"{seeker.first_name} {seeker.last_name}",
                        "phone": seeker.phone,
                        "email": seeker.email,
                        "address": seeker.address
                    },
                    "volunteer": {
                        "name": f"{volunteer.first_name} {volunteer.last_name}",
                        "phone": volunteer.phone,
                        "email": volunteer.email,
                        "address": volunteer.address
                    }
                }
                matches.append(match_data)

    return matches

def match_availability(seeker, volunteer):
    # Days of the week
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    # Time slots to compare
    time_slots = ['all_day', 'morning', 'afternoon', 'evening']

    # Check for overlapping availability
    for day in days:
        for slot in time_slots:
            seeker_available = getattr(seeker, f"{day}_{slot}")
            volunteer_available = getattr(volunteer, f"{day}_{slot}")

            if seeker_available and volunteer_available:
                return True  # A match is found

    return False
