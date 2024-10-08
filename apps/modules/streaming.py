import os
import requests
import logging
from typing import Dict, Any

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
            wind_speed = round(weather_data['wind']['speed'] * 3.6, 1)  # Convert m/s to km/h
            wind_direction = weather_data['wind']['deg']
            wind_direction_cardinal = WeatherData.deg_to_cardinal(wind_direction)

            # Generate advice
            advice = WeatherData.get_advice(temp)

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
    def get_advice(temp: float) -> str:
        if temp < -10:
            return "Il fait extrêmement froid aujourd'hui. Portez des vêtements très chauds et évitez les sorties prolongées."
        elif -10 <= temp < 0:
            return "Il fait très froid. Habillez-vous en plusieurs couches pour rester au chaud."
        elif 0 <= temp < 10:
            return "Il fait frais. Portez une veste chaude."
        elif 10 <= temp < 20:
            return "La température est agréable. Une veste légère ou un pull suffira."
        elif 20 <= temp < 30:
            return "Il fait chaud. Portez des vêtements légers et buvez beaucoup d'eau."
        elif 30 <= temp < 40:
            return "Il fait très chaud. Restez à l'ombre et buvez beaucoup d'eau."
        else:
            return "Il fait extrêmement chaud. Prenez des mesures pour vous protéger de la chaleur excessive."

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

class RecosanteAPI:
    API_URL = "https://api.recosante.beta.gouv.fr/v1/"
    
    def __init__(self, insee_code: str = '75056'):
        self.params = {
            'insee': insee_code,
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
        # Handle missing data with default values
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