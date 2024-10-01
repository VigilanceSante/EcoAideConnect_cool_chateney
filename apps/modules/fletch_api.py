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
            max_temp = round(weather_data['main']['temp_max'], 1)
            min_temp = round(weather_data['main']['temp_min'], 1)
            feel_like = round(weather_data['main']['feels_like'], 1)

            # Conversion de la direction du vent en cardinal
            wind_speed = round(weather_data['wind']['speed'] * 3.6, 1)
            wind_direction = weather_data['wind']['deg']
            wind_direction_cardinal = WeatherData.deg_to_cardinal(wind_direction)

            # Récupération des données de pollution
            pollution_data = PollutionData.get_pollution_data()
            pollution_index = pollution_data.get('indice', 'Non disponible')

            # Génération des conseils
            advice = WeatherData.get_advice(temp, pollution_index)

            return {
                'temperature': temp,
                'location': location,
                'description': description,
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
    def get_advice(temp: float, pollution_index: str) -> str:
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

        # Conseils basés sur l'indice de pollution
        pollution_advice = {
            'Bonne': "L'air est de bonne qualité. Profitez de votre journée à l'extérieur.",
            'Moyenne': "L'air est de qualité moyenne. Faites attention si vous êtes sensible aux allergies.",
            'Dégradée': "L'air est dégradé. Limitez les activités physiques en extérieur, surtout pour les personnes sensibles.",
            'Mauvaise': "L'air est de mauvaise qualité. Évitez les activités physiques à l'extérieur et restez à l'intérieur si possible.",
            'Très mauvaise': "L'air est très mauvais. Restez à l'intérieur et utilisez un purificateur d'air si disponible.",
            "Extrêmement mauvaise" : "L'air est extrêmement mauvais. Évitez de sortir et portez un masque si vous devez absolument sortir."
        }

        advice.append(pollution_advice.get(pollution_index, "État de l'air non précisé, restez vigilant."))

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
            5: 'Très mauvaise',
            6: 'Extrêmement mauvaise'
        }
        return mapping.get(value, 'Extrêmement mauvaise' if value not in mapping else 'Non disponible')


class CombinedData(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        weather_data = WeatherData().get_weather()
        pollution_data = PollutionData.get_pollution_data()

        # Fonction pour définir la classe CSS en fonction de la qualité de l'air
        def get_class_for_quality(quality):
            if quality == 'Bonne':
                return 'bonne'
            elif quality == 'Moyenne':
                return 'moyenne'
            elif quality == 'Dégradée':
                return 'degradee'
            elif quality == 'Mauvaise':
                return 'mauvaise'
            elif quality == 'Très mauvaise':
                return 'tres-mauvaise'
            else:
                return ''  # Si aucune correspondance

        # Ajout de la classe CSS à chaque polluant
        pollution_data['pm10_class'] = get_class_for_quality(pollution_data['PM10'])
        pollution_data['pm25_class'] = get_class_for_quality(pollution_data['PM25'])
        pollution_data['o3_class'] = get_class_for_quality(pollution_data['O3'])
        pollution_data['no2_class'] = get_class_for_quality(pollution_data['NO2'])
        pollution_data['so2_class'] = get_class_for_quality(pollution_data['SO2'])
        pollution_data['indice_class'] = get_class_for_quality(pollution_data['indice'])

        # Mise à jour du contexte avec les données météorologiques et de pollution
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