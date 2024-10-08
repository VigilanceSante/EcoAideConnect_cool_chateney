import logging
from typing import Dict, Any
from django.views.generic import TemplateView
from apps.modules.streaming import WeatherData, RecosanteAPI
from web_project import TemplateLayout

logger = logging.getLogger(__name__)

class CombinedData(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        weather_data = kwargs.get('weather_data', {})
        pollution_data = kwargs.get('pollution_data', {})
        pollen_data = kwargs.get('pollen_data', {})
        meteo_data = kwargs.get('meteo_data', {})

        # Function to map air quality to CSS classes
        def get_class_for_quality(quality: str) -> str:
            quality_to_class = {
                'Faible': 'faible',
                'Moyen': 'moyen',
                'Dégradé': 'degrade',
                'Mauvais': 'mauvais',
                'Très mauvais': 'tres-mauvais',
                'Aucun conseil disponible': 'default-class',
                'N/A': 'default-class',
            }
            return quality_to_class.get(quality, 'default-class')

        # Function to map pollen level to CSS classes
        def get_class_for_pollen(level: str) -> str:
            pollen_to_class = {
                'Faible': 'faible',
                'Moyen': 'moyen',
                'Dégradé': 'degrade',
                'Mauvais': 'mauvais',
                'Très mauvais': 'tres-mauvais',
            }
            return pollen_to_class.get(level, 'default-class')

        # Relevant keys for pollution and pollen data
        pollution_quality_keys = ['advice', 'label', 'level']
        pollen_quality_keys = ['advice']

        # Apply CSS classes to relevant pollution_data keys
        for key in pollution_quality_keys:
            value = pollution_data.get(key)
            if isinstance(value, str):
                class_value = get_class_for_quality(value)
                pollution_data[f'{key.lower()}_class'] = class_value
                logger.debug(f"Pollution - Key: {key}, Value: {value}, Class: {class_value}")
            else:
                if value is not None:
                    logger.warning(f"Pollution data key '{key}' has unexpected type: {type(value)}. Value: {value}")
                pollution_data[f'{key.lower()}_class'] = 'default-class'

        # Apply CSS classes to relevant pollen_data keys
        for key in pollen_quality_keys:
            value = pollen_data.get(key)
            if isinstance(value, str):
                class_value = get_class_for_pollen(value)
                pollen_data[f'{key.lower()}_class'] = class_value
                logger.debug(f"Pollen - Key: {key}, Value: {value}, Class: {class_value}")
            else:
                if value is not None:
                    logger.warning(f"Pollen data key '{key}' has unexpected type: {type(value)}. Value: {value}")
                pollen_data[f'{key.lower()}_class'] = 'default-class'

        # Generate CSS classes for weather_data if description exists
        if weather_data.get('description'):
            description_to_class = {
                'Ciel dégagé': 'clear',
                'Nuageux': 'cloudy',
                'Pluie': 'rainy',
                'Orage': 'stormy',
                'Neige': 'snowy',
            }
            description = weather_data.get('description')
            weather_data['description_class'] = description_to_class.get(description, 'default-class')
        else:
            weather_data['description_class'] = 'default-class'

        # Generate CSS classes for temperatures
        temp = weather_data.get('temperature')
        if isinstance(temp, (int, float)):
            if temp < 0:
                weather_data['max_temp_class'] = 'cold'
                weather_data['min_temp_class'] = 'cold'
            elif temp < 20:
                weather_data['max_temp_class'] = 'cool'
                weather_data['min_temp_class'] = 'cool'
            else:
                weather_data['max_temp_class'] = 'warm'
                weather_data['min_temp_class'] = 'warm'
        else:
            weather_data['max_temp_class'] = 'default-class'
            weather_data['min_temp_class'] = 'default-class'

        # Update the context with processed data
        context.update({
            'weather_data': weather_data,
            'pollution_data': pollution_data,
            'pollen_data': pollen_data,
            'meteo_data': meteo_data,
        })
        return context

    def get(self, request, *args, **kwargs):
        try:
            lat = float(request.GET.get('lat', 48.7651))
            lon = float(request.GET.get('lon', 2.2666))
            logger.debug(f"Received parameters - Latitude: {lat}, Longitude: {lon}")
        except ValueError:
            logger.error("Parameters 'lat' and 'lon' must be numbers.")
            lat, lon = 48.7651, 2.2666  # Default values

        # Fetch weather data
        weather_data_instance = WeatherData(lat=lat, lon=lon)
        try:
            weather_data = weather_data_instance.get_weather()
            logger.debug(f"Weather data retrieved: {weather_data}")
        except Exception as e:
            logger.error(f"Error retrieving weather data: {e}")
            weather_data = weather_data_instance._default_weather_response()

        # Fetch Recosante data
        recosante_api = RecosanteAPI()
        recosante_data = recosante_api.fetch_data()
        parsed_data = recosante_api.parse_data(recosante_data)
        logger.debug(f"Recosante data retrieved: {parsed_data}")

        # Extract specific data
        pollution_data = parsed_data.get('episodes_pollution', {})
        pollen_data = parsed_data.get('raep', {})
        meteo_data = parsed_data.get('vigilance_meteo', {})

        # Prepare context with retrieved data
        context = self.get_context_data(
            weather_data=weather_data,
            pollution_data=pollution_data,
            pollen_data=pollen_data,
            meteo_data=meteo_data
        )
 
        logger.debug(f"Final context prepared: {context}")

        return self.render_to_response(context)