from django.views.generic import TemplateView
from web_project import TemplateLayout
import requests
import json
from typing import Dict, Any

class WeatherData:
    def __init__(self, lat: float = 48.7651, lon: float = 2.2666):
        self.lat = lat
        self.lon = lon

    def set_location(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def get_weather(self) -> Dict[str, Any]:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid=7b7ff4bb3216cc1bb91bfff3f7ee3f25&units=metric&lang=fr'
        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()

            # Extraction et formatage des données
            temp = round(weather_data['main']['temp'], 1)
            location = weather_data['name']
            description = weather_data['weather'][0]['description'].capitalize()
            humidity = weather_data['main']['humidity']
            wind_speed = round(weather_data['wind']['speed'] * 3.6, 1)
            wind_direction = weather_data['wind']['deg']
            max_temp = round(weather_data['main']['temp_max'], 1)
            min_temp = round(weather_data['main']['temp_min'], 1)
            feel_like = round(weather_data['main']['feels_like'], 1)

            # Conversion de la direction du vent en cardinal
            wind_direction_cardinal = WeatherData.deg_to_cardinal(wind_direction)

            # Génération des conseils
            advice = WeatherData.get_advice(temp, description, humidity, wind_speed)

            return {
                'temperature': temp,
                'location': location,
                'description': description,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction_cardinal,
                'max_temp': max_temp,
                'min_temp': min_temp,
                'feel_like': feel_like,
                'advice': advice
            }

        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return {
                'temperature': 'N/A',
                'location': 'Inconnue',
                'description': 'Aucune donnée disponible',
                'humidity': 'N/A',
                'wind_speed': 'N/A',
                'wind_direction': 'N/A',
                'max_temp': 'N/A',
                'min_temp': 'N/A',
                'feel_like': 'N/A',
                'advice': 'Aucun conseil disponible pour le moment.'
            }

    @staticmethod
    def deg_to_cardinal(deg: int) -> str:
        directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
        deg = deg % 360
        ix = int((deg + 22.5) / 45) % 8
        return directions[ix]

    @staticmethod
    def get_advice(temp: float, description: str, humidity: int, wind_speed: float) -> str:
        advice = []

        # Conseils basés sur la température
        if temp < -10:
            advice.append("Il fait extrêmement froid aujourd'hui. Portez des vêtements très chauds et évitez les sorties prolongées.")
        elif -10 <= temp < 0:
            advice.append("Il fait très froid. Habillez-vous en plusieurs couches pour rester au chaud.")
        elif 0 <= temp < 10:
            advice.append("Il fait frais. Portez une veste chaude.")
        elif 10 <= temp < 20:
            advice.append("La température est agréable. Une veste légère ou un pull suffira.")
        elif 20 <= temp < 30:
            advice.append("Il fait chaud. Portez des vêtements légers et buvez beaucoup d'eau.")
        elif 30 <= temp < 40:
            advice.append("Il fait très chaud. Restez à l'ombre et buvez beaucoup d'eau.")
        else:
            advice.append("Il fait extrêmement chaud. Prenez des mesures pour vous protéger de la chaleur excessive.")

        # Conseils basés sur la description météo
        description_advice = {
            'Ciel dégagé': "Le ciel est dégagé. Protégez-vous avec de la crème solaire et des lunettes de soleil.",
            'Peu nuageux': "Il y a quelques nuages. Profitez de la journée avec des vêtements appropriés.",
            'Nuages épars': "Il y a des nuages épars. Vérifiez la météo régulièrement pour les changements.",
            'Nuages fragmentés': "Il y a des nuages fragmentés. Aucun changement majeur attendu.",
            'Averse de pluie': "Il y a une averse de pluie. Prenez un parapluie ou un imperméable.",
            'Orage': "Il y a un orage. Restez à l'intérieur et évitez les activités extérieures.",
            'Neige': "Il neige. Conduisez prudemment et restez au chaud.",
            'Brume': "Il y a de la brume. Conduisez prudemment et maintenez une bonne visibilité."
        }

        advice.append(description_advice.get(description, "Des conditions météorologiques variées."))

        # Conseils basés sur l'humidité
        if int(humidity) > 80:
            advice.append("L'humidité est élevée. Vous pourriez vous sentir collant et il pourrait y avoir un risque de moisissure.")
        elif int(humidity) < 30:
            advice.append("L'humidité est basse. Utilisez une crème hydratante pour éviter la sécheresse de la peau.")

        # Conseils basés sur la vitesse du vent
        if wind_speed > 50:
            advice.append("Le vent est très fort. Évitez les activités en extérieur et sécurisez les objets légers.")
        elif wind_speed > 20:
            advice.append("Il y a du vent. Faites attention aux rafales et sécurisez vos affaires.")

        return " ".join(advice)

class PollutionData:
    @staticmethod
    def get_pollution_data() -> Dict[str, str]:
        url = (
            "https://magellan.airparif.asso.fr/geoserver/siteweb/wms?"
            "SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&TRANSPARENT=true&FORMAT=image%2Fjpeg&"
            "QUERY_LAYERS=siteweb%3Avue_indice_atmo_2020_com_jp1&LAYERS=siteweb%3Avue_indice_atmo_2020_com_jp1&"
            "INFO_FORMAT=application%2Fjson&FEATURE_COUNT=50&Y=1&X=1&SRS=EPSG%3A27572&WIDTH=3&HEIGHT=3&"
            "BBOX=595114.0466738944%2C2419223.466502076%2C595214.0466738944%2C2419323.466502076&AUTHKEY=YOUR_API_KEY"
        )

        pollution_data = {
            'indice': 'Non disponible',
            'O3': 'Non disponible',
            'NO2': 'Non disponible',
            'PM10': 'Non disponible',
            'PM25': 'Non disponible',
            'SO2': 'Non disponible'
        }

        try:
            # Fetch data from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad HTTP status codes

            # Load the response content as JSON
            data = response.json()

            # Extract values and populate the dictionary
            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                pollution_data['indice'] = properties.get('indice', 'Non disponible')
                pollution_data['O3'] = properties.get('o3', 'Non disponible')
                pollution_data['NO2'] = properties.get('no2', 'Non disponible')
                pollution_data['PM10'] = properties.get('pm10', 'Non disponible')
                pollution_data['PM25'] = properties.get('pm25', 'Non disponible')
                pollution_data['SO2'] = properties.get('so2', 'Non disponible')
                # Since we are interested in the first feature only, we break after the first iteration
                break

            # Convert numeric values to text for all pollutants
            pollution_data = {key: PollutionData.numeric_to_text(value) for key, value in pollution_data.items()}

        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        return pollution_data

    @staticmethod
    def numeric_to_text(value: Any) -> str:
        # Map numeric values to text descriptions
        mapping = {
            1: 'Bonne',
            2: 'Moyenne',
            3: 'Dégradée',
            4: 'Mauvaise',
            5: 'Très mauvaise'
        }
        return mapping.get(value, 'Extrêmement mauvaise' if value not in mapping else 'Non disponible')

class CombinedData(TemplateView):
    template_name = 'home_page.html'


    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        weather_data = WeatherData().get_weather()
        pollution_data = PollutionData.get_pollution_data()
        context.update(weather_data)
        context.update(pollution_data)
        return context

    def get(self, request, *args, **kwargs):
        lat = request.GET.get('lat', 48.7651)
        lon = request.GET.get('lon', 2.2666)
        weather_data_instance = WeatherData(lat=lat, lon=lon)
        weather_data = weather_data_instance.get_weather()
        pollution_data = PollutionData.get_pollution_data()
        context = self.get_context_data(weather_data=weather_data, pollution_data=pollution_data)
        return self.render_to_response(context)
