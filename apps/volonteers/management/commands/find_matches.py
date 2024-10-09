from django.core.management.base import BaseCommand
from apps.db_users.models import ContactForm
from django.db import transaction
from django.core.paginator import Paginator

class Command(BaseCommand):
    help = 'Find matches between seekers and volunteers based on availability.'

    def handle(self, *args, **kwargs):
        # Pagination to process seekers and volunteers in batches
        seeker_batch_size = 100  # Number of seekers to process at a time
        volunteer_batch_size = 500  # Number of volunteers to process at a time

        seekers = ContactForm.objects.filter(is_volunteer=False, buddy_id__isnull=True)
        volunteers = ContactForm.objects.filter(is_volunteer=True, buddy_id__isnull=True)

        seeker_paginator = Paginator(seekers, seeker_batch_size)
        volunteer_paginator = Paginator(volunteers, volunteer_batch_size)

        for seeker_page_num in seeker_paginator.page_range:
            seeker_page = seeker_paginator.page(seeker_page_num)
            for volunteer_page_num in volunteer_paginator.page_range:
                volunteer_page = volunteer_paginator.page(volunteer_page_num)
                
                matches = find_matches_with_info(seeker_page, volunteer_page)
                
                for match in matches:
                    seeker_info = match['seeker']
                    volunteer_info = match['volunteer']
                    self.stdout.write(
                        f"Seeker {seeker_info['name']} (Phone: {seeker_info['phone']}, Email: {seeker_info['email']}, Address: {seeker_info['address']}) matched with "
                        f"Volunteer {volunteer_info['name']} (Phone: {volunteer_info['phone']}, Email: {volunteer_info['email']}, Address: {volunteer_info['address']})"
                    )
                    
                    # Update the buddy_id field for each pair
                    try:
                        seeker = ContactForm.objects.get(id=seeker_info['id'])
                        volunteer = ContactForm.objects.get(id=volunteer_info['id'])

                        if not seeker.buddy_id and not volunteer.buddy_id:  # Ensure neither already has a buddy
                            with transaction.atomic():
                                seeker.buddy_id = str(volunteer.id)
                                volunteer.buddy_id = str(seeker.id)

                                seeker.save()
                                volunteer.save()
                        else:
                            print(f"Skipping: Seeker {seeker.id} or Volunteer {volunteer.id} already has a buddy.")
                    
                    except ContactForm.DoesNotExist:
                        print(f"Error: Seeker or Volunteer with given ID not found")

def find_matches_with_info(seekers, volunteers):
    matches = []

    # Compare availability and gather user information for matches
    for seeker in seekers:
        for volunteer in volunteers:
            if match_availability(seeker, volunteer):
                match_data = {
                    "seeker": {
                        "id": seeker.id,
                        "name": f"{seeker.first_name} {seeker.last_name}",
                        "phone": seeker.phone,
                        "email": seeker.email,
                        "address": seeker.address
                    },
                    "volunteer": {
                        "id": volunteer.id,
                        "name": f"{volunteer.first_name} {volunteer.last_name}",
                        "phone": volunteer.phone,
                        "email": volunteer.email,
                        "address": volunteer.address
                    }
                }
                matches.append(match_data)
                break  # Exit once a match is found for this seeker

    return matches

def match_availability(seeker, volunteer):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    time_slots = ['all_day', 'morning', 'afternoon', 'evening']

    # Check for overlapping availability
    for day in days:
        for slot in time_slots:
            seeker_available = getattr(seeker, f"{day}_{slot}")
            volunteer_available = getattr(volunteer, f"{day}_{slot}")

            if seeker_available and volunteer_available:
                print(f"Match found on {day} {slot} between {seeker.first_name} and {volunteer.first_name}")
                return True

    return False