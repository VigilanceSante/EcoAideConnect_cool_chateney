import requests

# Make the API call
response = requests.get("https://api-adresse.data.gouv.fr/search/?q=Châtenay-Malabry&postcode=92290&limit=100")

# Convert the response to JSON
data = response.json()

# Display the data
data
print(data)
