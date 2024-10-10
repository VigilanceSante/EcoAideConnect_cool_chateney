import os
import requests
import logging
from typing import Dict, Any
import dotenv
from django.views.generic import TemplateView
from apps.modules.forcast import WeatherData, RecosanteAPI
from web_project import TemplateLayout

# Load environment variables from a .env file
dotenv.load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class CombinedData(TemplateView):
    def get_context_data(self, **kwargs):
        # Initialize context using TemplateLayout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pollen_data = kwargs.get('pollen_data', {})
        # Fetch weather data
        lat = self.request.GET.get('lat', 48.7651)
        lon = self.request.GET.get('lon', 2.2666)

        try:
            weather_data_instance = WeatherData(lat=float(lat), lon=float(lon))
            weather_data = weather_data_instance.get_weather_forecast()
        except ValueError as e:
            logger.error(f"Failed to fetch weather data: {e}")
            weather_data = {
                'plus1H': {'feels_like': 'N/A', 'temperature': 'N/A'},
                'plus24H': {'feels_like': 'N/A', 'temperature': 'N/A'},
                'min_temp': 'N/A',
                'max_temp': 'N/A'
            }

        # Fetch pollution and pollen data
        recosante_api = RecosanteAPI()
        recosante_data = recosante_api.fetch_data()

        # Extract pollution and pollen data
        pollution_data = recosante_data.get('indice_atmo', {})
        pollen_levels = pollen_data.get('pollen_levels', {})
        context['pollens'] = [{'label': key.capitalize(), 'niveau': value} for key, value in pollen_levels.items()]

        episodes_pollution_data = recosante_data.get('episodes_pollution', {}).get('details', [])

        # Prepare context data
        context['temperature'] = weather_data.get('plus1H', {}).get('temperature', 'N/A')
        context['plus1H'] = weather_data.get('plus1H', {})
        context['plus24H'] = weather_data.get('plus24H', {})

        # Pollutants (PM10, PM2.5, etc.)
        air_quality_levels = pollution_data.get('air_quality_levels', {})
        context['polluants'] = [{'label': key, 'niveau': value} for key, value in air_quality_levels.items()]

        # Extract values for each pollutant
        # Pollutants (PM10, PM2.5, etc.)
        air_quality_levels = pollution_data.get('air_quality_levels', {})
        context['polluants'] = [{'label': key, 'niveau': value} for key, value in air_quality_levels.items()]

        # Extract pollution episodes data
        episodes_pollution_data = recosante_data.get('episodes_pollution', {}).get('details', [])
        context['episodes_pollution_data'] = episodes_pollution_data

        # Extract episodes pollution data PM10
        context['episodde_PM10'] = [
            episode for episode in episodes_pollution_data if episode.get('label') == 'Particules PM10'
        ]
        # Extrat data for Ozone
        context['episodde_O3'] = [
            episode for episode in episodes_pollution_data if episode.get('label') == 'Ozone'
        ]
        # Extract data for NO2
        context['episodde_NO2'] = [
            episode for episode in episodes_pollution_data if episode.get('label') == 'Dioxyde d’azote'
        ]

        # Add weather forecast for the next 24 hours
        context['next_24H'] = weather_data.get('plus24H', {})

        return context

    def get(self, request, *args, **kwargs):
        lat = request.GET.get('lat', 48.7651)
        lon = request.GET.get('lon', 2.2666)
        
        # Fetch data
        weather_data_instance = WeatherData(lat=float(lat), lon=float(lon))
        weather_data = weather_data_instance.get_weather_forecast()

        recosante_api = RecosanteAPI()
        recosante_data = recosante_api.fetch_data()

        # Extract data
        pollution_data = recosante_data.get('indice_atmo', {})
        pollen_data = recosante_data.get('raep', {})
        episodes_pollution_data = recosante_data.get('episodes_pollution', {})

        # Prepare the context
        context = self.get_context_data(
            weather_data=weather_data,
            pollution_data=pollution_data,
            pollen_data=pollen_data,
            episodes_pollution_data=episodes_pollution_data
        )

        return self.render_to_response(context)