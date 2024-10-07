import os
import requests
import logging
from typing import Dict, Any
import dotenv
from web_project import TemplateLayout
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
        print(self.api_key)

    def set_location(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def get_weather_forecast(self) -> Dict[str, Any]:
        if not self.api_key:
            logger.error("OpenWeather API key is not set.")
            return self._default_weather_response()

        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
        print(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()

            list_data = weather_data.get('list', [])
            if len(list_data) < 24:
                logger.error("Not enough forecast data available to extract +1H and +24H data.")
                return self._default_weather_response()

            # Get the data for +1 hour and +24 hours (at 3-hour intervals, index 8 roughly represents +24 hours)
            next_hour_data = list_data[1]
            next_24_hour_data = list_data[8]  

            next_hour_info = {
                "datetime": next_hour_data.get("dt_txt", "N/A"),
                "temperature": next_hour_data["main"].get("temp", "N/A"),
                "feels_like": next_hour_data["main"].get("feels_like", "N/A"),
                "weather": next_hour_data["weather"][0].get("description", "N/A"),
                "wind_speed": next_hour_data["wind"].get("speed", "N/A"),
            }

            next_24_hour_info = {
                "datetime": next_24_hour_data.get("dt_txt", "N/A"),
                "temperature": next_24_hour_data["main"].get("temp", "N/A"),
                "feels_like": next_24_hour_data["main"].get("feels_like", "N/A"),
                "weather": next_24_hour_data["weather"][0].get("description", "N/A"),
                "wind_speed": next_24_hour_data["wind"].get("speed", "N/A"),
            }

            return {
                'plus1H': next_hour_info,
                'plus24H': next_24_hour_info
            }

        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return self._default_weather_response()

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
                    'indice': properties.get('indice', 'Faible'),
                    'O3': properties.get('o3', 'Faible'),
                    'NO2': properties.get('no2', 'Faible'),
                    'PM10': properties.get('pm10', 'Faible'),
                    'PM25': properties.get('pm25', 'Faible'),
                    'SO2': properties.get('so2', 'Faible')
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
        text = mapping.get(value, 'Faible')
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
            'indice': 'Faible',
            'O3': 'Faible',
            'NO2': 'Faible',
            'PM10': 'Faible',
            'PM25': 'Faible',
            'SO2': 'Faible'
        }
        logger.debug("Using default pollution response.")
        return default_response
class PollenData:
    @staticmethod
    def get_pollen_data(lat: float, lon: float) -> Dict[str, str]:
        api_key = os.getenv('AMBEE_API_KEY')
        if not api_key:
            logger.error("Ambee API key is not set.")
            return {'pollen_risk': 'Faible'}

        url = 'https://api.ambeedata.com/forecast/pollen/by-lat-lng'
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

            tree_pollen_risk = data['data'][0]['Risk']['tree_pollen'] if data.get('data') else "Faible"
            grass_pollen_risk = data['data'][0]['Risk']['grass_pollen'] if data.get('data') else "Faible"
            # translate the risk level to French
            tree_pollen_risk = {
                'Low': 'Faible',
                'Medium': 'Moyen',
                'High': 'Élevé',
                'Very High': 'Très élevé'
            }.get(tree_pollen_risk, 'Faible')
            grass_pollen_risk = {
                'Low': 'Faible',
                'Medium': 'Moyen',
                'High': 'Élevé',
                'Very High': 'Très élevé'
            }.get(grass_pollen_risk, 'Faible')
     
            return {
                'tree_pollen_risk': tree_pollen_risk,
                'grass_pollen_risk': grass_pollen_risk
            }
            

        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return {'pollen_risk': 'Faible'}

  
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
        weather_data = weather_data_instance.get_weather_forecast()
        pollution_data = PollutionData.get_pollution_data()
        pollen_data = PollenData.get_pollen_data(lat, lon)

        context = self.get_context_data(weather_data=weather_data, pollution_data=pollution_data, pollen_data=pollen_data)
        return self.render_to_response(context)