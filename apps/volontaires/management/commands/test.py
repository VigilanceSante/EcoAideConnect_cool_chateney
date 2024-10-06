import requests
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Fetch data from the API and display it'

    def handle(self, *args, **kwargs):
        # Make the API call
        response = requests.get("https://api-adresse.data.gouv.fr/search/?q=Châtenay-Malabry&postcode=92290&limit=100")

        # Convert the response to JSON
        data = response.json()

        # Print the data
        self.stdout.write(self.style.SUCCESS('Data fetched successfully'))
        print(data)
