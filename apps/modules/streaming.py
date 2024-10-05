import os
from django.views.generic import TemplateView
from web_project import TemplateLayout
import requests
import json
import logging
from typing import Dict, Any


# Set up logging
logger = logging.getLogger(__name__)

class WeatherData:
    def __init__(self, lat: float = 48.7651, lon: float = 2.2666):
        self.lat = lat
        self.lon = lon
        self.api_key = os.getenv('OPENWEATHER_API_KEY')

    def set_location(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def get_weather(self) -> Dict[str, Any]:
        if not self.api_key:
            logger.error("OpenWeather API key is not set.")
            return self._default_weather_response()

        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric&lang=fr'
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()

            # Extract and format weather data
            temp = round(weather_data['main']['temp'], 1)
            location = weather_data['name']
            description = weather_data['weather'][0]['description'].capitalize()
            max_temp = round(weather_data['main']['temp_max'], 1)
            min_temp = round(weather_data['main']['temp_min'], 1)
            feel_like = round(weather_data['main']['feels_like'], 1)
            wind_speed = round(weather_data['wind']['speed'] * 3.6, 1)
            wind_direction = weather_data['wind']['deg']
            wind_direction_cardinal = WeatherData.deg_to_cardinal(wind_direction)

            # Get pollution data
            pollution_data = PollutionData.get_pollution_data()
            pollution_index = pollution_data.get('indice', 'Non disponible')

            # Generate advice
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
            logger.error(f"HTTP Request failed: {e}")
            return self._default_weather_response()

    @staticmethod
    def deg_to_cardinal(deg: int) -> str:
        directions = ['Nord', 'Nord-Est', 'Est', 'Sud-Est', 'Sud', 'Sud-Ouest', 'Ouest', 'Nord-Ouest']
        deg = deg % 360
        ix = int((deg + 22.5) / 45) % 8
        return directions[ix]

    @staticmethod
    def get_advice(temp: float, pollution_index: str) -> str:
        advice = []

        # Temperature-based advice
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

        # Pollution-based advice
        pollution_advice = {
            'Bonne': "L'air est de bonne qualité. Profitez de votre journée à l'extérieur.",
            'Moyenne': "L'air est de qualité moyenne. Faites attention si vous êtes sensible aux allergies.",
            'Dégradée': "L'air est dégradé. Limitez les activités physiques en extérieur, surtout pour les personnes sensibles.",
            'Mauvaise': "L'air est de mauvaise qualité. Évitez les activités physiques à l'extérieur et restez à l'intérieur si possible.",
            'Très mauvaise': "L'air est très mauvais. Restez à l'intérieur et utilisez un purificateur d'air si disponible.",
            "Extrêmement mauvaise": "L'air est extrêmement mauvais. Évitez de sortir et portez un masque si vous devez absolument sortir."
        }

        advice.append(pollution_advice.get(pollution_index, "État de l'air non précisé, restez vigilant."))

        return " ".join(advice)

    @staticmethod
    def _default_weather_response() -> Dict[str, Any]:
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



class PollutionData:
    @staticmethod
    def get_pollution_data() -> Dict[str, str]:
        """
        Fetches pollution data from the Airparif API and converts numeric indices to textual descriptions.
        
        Returns:
            Dict[str, str]: A dictionary containing pollution metrics with textual descriptions.
        """
        auth_key = os.getenv('AIRPARIF_API_KEY')
        if not auth_key:
            logger.error("Airparif API key is not set.")
            return PollutionData._default_pollution_response()

        url = (
            "https://magellan.airparif.asso.fr/geoserver/siteweb/wms?"
            "SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&TRANSPARENT=true&FORMAT=image%2Fjpeg&"
            "QUERY_LAYERS=siteweb%3Avue_indice_atmo_2020_com_jp1&LAYERS=siteweb%3Avue_indice_atmo_2020_com_jp1&"
            "INFO_FORMAT=application%2Fjson&FEATURE_COUNT=50&Y=1&X=1&SRS=EPSG%3A27572&WIDTH=3&HEIGHT=3&"
            f"BBOX=595114.0466738944%2C2419223.466502076%2C595214.0466738944%2C2419323.466502076&AUTHKEY={auth_key}"
        )

        # Initialize pollution_data with default values to prevent UnboundLocalError
        pollution_data = PollutionData._default_pollution_response()
        logger.debug("Initialized pollution_data with default values.")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Received pollution data response: {data}")

            features = data.get("features", [])
            if not features:
                logger.warning("No features found in pollution data response.")
                # pollution_data remains as default
            else:
                # Extract values from the first feature
                properties = features[0].get("properties", {})
                logger.debug(f"Extracted properties from first feature: {properties}")

                # Update pollution_data with actual values if available
                pollution_data.update({
                    'indice': properties.get('indice', 'Non disponible'),
                    'O3': properties.get('o3', 'Non disponible'),
                    'NO2': properties.get('no2', 'Non disponible'),
                    'PM10': properties.get('pm10', 'Non disponible'),
                    'PM25': properties.get('pm25', 'Non disponible'),
                    'SO2': properties.get('so2', 'Non disponible')
                })
                logger.debug(f"Updated pollution_data with API values: {pollution_data}")

        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        # Convert numeric pollution data to textual descriptions
        converted_data = {key: PollutionData.numeric_to_text(value) for key, value in pollution_data.items()}
        logger.debug(f"Converted pollution_data to text: {converted_data}")

        return converted_data

    @staticmethod
    def numeric_to_text(value: Any) -> str:
        """
        Converts numeric pollution indices to their corresponding textual descriptions.
        
        Args:
            value (Any): The numeric pollution index.
        
        Returns:
            str: The textual description of the pollution index.
        """
        mapping = {
            1: 'Faible',
            2: 'Moyen',
            3: 'Dégradé',
            4: 'Mauvaise',
            5: 'Très mauvais',
            6: 'Extrêmement mauvais'
        }
        text = mapping.get(value, 'Non disponible')
        logger.debug(f"Converted numeric value '{value}' to text '{text}'.")
        return text

    @staticmethod
    def _default_pollution_response() -> Dict[str, str]:
        """
        Provides a default pollution data response when API data is unavailable.
        
        Returns:
            Dict[str, str]: A dictionary with default pollution metrics.
        """
        default_response = {
            'indice': 'Non disponible',
            'O3': 'Non disponible',
            'NO2': 'Non disponible',
            'PM10': 'Non disponible',
            'PM25': 'Non disponible',
            'SO2': 'Non disponible'
        }
        logger.debug("Using default pollution response.")
        return default_response
class PollenData:
    @staticmethod
    def get_pollen_data(lat: float, lon: float) -> Dict[str, str]:
        api_key = os.getenv('AMBEE_API_KEY')
        if not api_key:
            logger.error("Ambee API key is not set.")
            return {'pollen_risk': 'Non disponible'}

        url = 'https://api.ambeedata.com/latest/pollen/by-lat-lng'
        headers = {
            'x-api-key': api_key,
            'Content-type': 'application/json'
        }
        params = {
            'lat': lat,
            'lng': lon
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            tree_pollen_risk = data['data'][0]['Risk']['tree_pollen'] if data.get('data') else "Non disponible"
            grass_pollen_risk = data['data'][0]['Risk']['grass_pollen'] if data.get('data') else "Non disponible"
            # translate the risk level to French
            tree_pollen_risk = {
                'Low': 'Faible',
                'Medium': 'Moyen',
                'High': 'Élevé',
                'Very High': 'Très élevé'
            }.get(tree_pollen_risk, 'Non disponible')
            grass_pollen_risk = {
                'Low': 'Faible',
                'Medium': 'Moyen',
                'High': 'Élevé',
                'Very High': 'Très élevé'
            }.get(grass_pollen_risk, 'Non disponible')
     
            return {
                'tree_pollen_risk': tree_pollen_risk,
                'grass_pollen_risk': grass_pollen_risk
            }
            

        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return {'pollen_risk': 'Non disponible'}


class CombinedData(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        weather_data = kwargs.get('weather_data', {})
        pollution_data = kwargs.get('pollution_data', {})
        pollen_data = kwargs.get('pollen_data', {})

        # Function to define CSS class based on air quality
        def get_class_for_quality(quality):
            return {
                'Faible': 'faible',
                'Moyen': 'moyen',
                'Dégradé': 'degrade',
                'Mauvais': 'mauvais',
                'Très mauvais': 'tres-mauvais',
            }.get(quality, '')
        def get_class_for_pollen(level):
            return {
                'Faible': 'faible',
                'Moyen': 'moyen',
                'Dégradé': 'degrade',
                'Mauvais': 'mauvais',
                'Très mauvais': 'tres-mauvais',
            }.get(level, 'default_class')  # consider adding a default class to catch errors


        for key in list(pollution_data.keys()):  # Use list to create a copy of keys
            pollution_data[f'{key.lower()}_class'] = get_class_for_quality(pollution_data[key])

        # Apply CSS classes to each pollen risk level
        for key in list(pollen_data.keys()):  # Use list to create a copy of keys
            pollen_data[f'{key.lower()}_class'] = get_class_for_pollen(pollen_data[key])

        # Update the context with weather, pollution, and pollen data
        context.update(weather_data)
        context.update(pollution_data)
        context.update(pollen_data)
        return context

    def get(self, request, *args, **kwargs):
        lat = float(request.GET.get('lat', 48.7651))
        lon = float(request.GET.get('lon', 2.2666))
        weather_data_instance = WeatherData(lat=lat, lon=lon)
        weather_data = weather_data_instance.get_weather()
        pollution_data = PollutionData.get_pollution_data()
        pollen_data = PollenData.get_pollen_data(lat, lon)

        context = self.get_context_data(weather_data=weather_data, pollution_data=pollution_data, pollen_data=pollen_data)
        return self.render_to_response(context)