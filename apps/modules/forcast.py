import os
import requests
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import dotenv
from django.views.generic import TemplateView

# Load environment variables from a .env file
dotenv.load_dotenv() 

# Set up logging
logger = logging.getLogger(__name__)

class WeatherData:
    def __init__(self, lat: float = 48.7651, lon: float = 2.2666):
        self.lat = lat
        self.lon = lon
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            logger.error("OpenWeather API key is not set.")
            raise ValueError("API key must be set in the environment variables.")

    def set_location(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def get_weather_forecast(self) -> Dict[str, Any]:
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric&lang=fr"
        logger.debug(f"Fetching weather data from: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()
            logger.debug(f"Weather data response: {weather_data}")  # Log the entire response

            # Check if we have enough data
            list_data = weather_data.get('list', [])
            if len(list_data) < 24:
                logger.error("Not enough forecast data available.")
                return self._default_weather_response()

            # Get the data for +1 hour and +24 hours
            next_hour_data = list_data[1]  # Ensure this index exists
            next_24_hour_data = list_data[8]  # Ensure this index exists

            # Extract relevant information
            next_hour_info = self._extract_weather_info(next_hour_data)
            next_24_hour_info = self._extract_weather_info(next_24_hour_data)

            # Add min_temp and max_temp based on the day's forecast
            min_temp = min(data['main']['temp'] for data in list_data)
            max_temp = max(data['main']['temp'] for data in list_data)

            return {
                'plus1H': next_hour_info,
                'plus24H': next_24_hour_info,
                'min_temp': min_temp,
                'max_temp': max_temp
            }

        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return self._default_weather_response()
    def _extract_weather_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to extract weather information from API response."""
        return {
            "datetime": data.get("dt_txt", "N/A"),
            "temperature": data["main"].get("temp", "N/A"),
            "feels_like": data["main"].get("feels_like", "N/A"),
            "weather": data["weather"][0].get("description", "N/A"),
            "wind_speed": data["wind"].get("speed", "N/A"),
        }

    @staticmethod
    def _default_weather_response() -> Dict[str, Any]:
        return {
            'plus1H': {
                'temperature': 'N/A',
                'description': 'Aucune donnée disponible',
                'wind_speed': 'N/A',
            },
            'plus24H': {
                'temperature': 'N/A',
                'description': 'Aucune donnée disponible',
                'wind_speed': 'N/A',
            }
        }

class RecosanteAPI:
    API_URL = "https://api.recosante.beta.gouv.fr/v1/"
    
    def __init__(self, insee_code: str = '75056'):
        # Calculate J+1 date
        j_plus_1_date = datetime.now() + timedelta(days=1)
        self.date = j_plus_1_date.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
        self.params = {
            'insee': insee_code,
            'date': self.date,  # Use J+1 date
            'time': '12:00',  # Set a default time
            'show_raep': 'true',  # Pollen data
            'show_indice_uv': 'true',  # UV Index data
        }

    def fetch_data(self) -> Dict[str, Any]:
        try:
            response = requests.get(self.API_URL, params=self.params)
            response.raise_for_status()
            return self.parse_data(response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données de l'API Recosante: {e}")
            return {}

    def parse_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'commune': data.get('commune', {}),
            'episodes_pollution': self.parse_episodes_pollution(data.get('episodes_pollution', {})),
            'indice_atmo': self.parse_indice_atmo(data.get('indice_atmo', {})),
            'indice_uv': self.parse_indice_uv(data.get('indice_uv', {})),
            'raep': self.parse_raep(data.get('raep', {})),
            'vigilance_meteo': self.parse_vigilance_meteo(data.get('vigilance_meteo', {}))
        }

    def parse_episodes_pollution(self, pollution_data: Dict[str, Any]) -> Dict[str, Any]:
        details = pollution_data.get('indice', {}).get('details', [])
        return {
            'label': pollution_data.get('indice', {}).get('label', 'Aucune donnée'),
            'details': [{'label': item.get('label', 'Inconnu'), 'level': item.get('level', 'N/A')} for item in details],
            'sources': pollution_data.get('sources', []),
            'validity': pollution_data.get('validity', {}),
        }

    def parse_indice_atmo(self, atmo_data: Dict[str, Any]) -> Dict[str, Any]:
        air_quality_levels = {pollutant: 'N/A' for pollutant in ['PM10', 'PM2,5', 'NO2', 'O3', 'SO2']}
        for detail in atmo_data.get('indice', {}).get('details', []):
            label = detail.get('label', '').upper()
            if label in air_quality_levels:
                air_quality_levels[label] = detail.get('indice', {}).get('label', 'N/A')

        return {
            'advice': atmo_data.get('advice', {}).get('main', 'Aucun conseil disponible'),
            'air_quality_levels': air_quality_levels,
            'overall_index': atmo_data.get('indice', {}).get('label', 'N/A')
        }

    def parse_raep(self, raep_data: Dict[str, Any]) -> Dict[str, Any]:
        pollen_levels = {}
        for detail in raep_data.get('indice', {}).get('details', []):
            pollen_levels[detail.get('label', '').lower()] = detail.get('indice', {}).get('label', 'N/A')

        return {
            'advice': raep_data.get('advice', {}).get('main', 'Aucun conseil lié au pollen disponible.'),
            'pollen_levels': pollen_levels
        }


    def parse_indice_uv(self, uv_data: Dict[str, Any]) -> Dict[str, Any]:
        advice = uv_data.get('advice', {}).get('main', 'Aucun conseil lié à l\'UV disponible.')
        return {
            'advice': advice,
            'label': uv_data.get('indice', {}).get('label', 'Indice UV inconnu'),
            'value': uv_data.get('indice', {}).get('value', 'N/A')
        }

    def parse_vigilance_meteo(self, meteo_data: Dict[str, Any]) -> Dict[str, Any]:
        vigilance_details = [{
            'label': detail['indice'].get('label', 'Inconnu'),
            'color': detail['indice'].get('color', 'Green'),
            'validity': {
                'start': detail['indice'].get('validity', {}).get('start', 'Heure de début non spécifiée'),
                'end': detail['indice'].get('validity', {}).get('end', 'Heure de fin non spécifiée')
            }
        } for detail in meteo_data.get('indice', {}).get('details', [])]

        return {
            'advice': meteo_data.get('advice', {}).get('main', 'Aucun conseil météo spécifique disponible.'),
            'details': vigilance_details
        }