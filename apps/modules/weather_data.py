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
            wind_speed = round(weather_data['wind']['speed'] * 3.6, 1)
            wind_direction = weather_data['wind']['deg']
            wind_direction_cardinal = WeatherData.deg_to_cardinal(wind_direction)

            # Get pollution data
            pollution_data = PollutionData.get_pollution_data()
            pollution_index = pollution_data.get('indice', 'Faible')

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
