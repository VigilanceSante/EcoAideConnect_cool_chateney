from django.views.generic import TemplateView
from apps.modules.streaming import WeatherData, RecosanteAPI
from web_project import TemplateLayout

class CombinedData(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Récupération des données météo, pollution et pollen
        weather_data = kwargs.get('weather_data', {})
        pollution_data = kwargs.get('pollution_data', {})
        pollen_data = kwargs.get('pollen_data', {})
        context['wind_speed'] = weather_data['wind_speed']  # e.g., from your WeatherData class
        context['min_temp'] = weather_data['min_temp']
        context['max_temp'] = weather_data['max_temp']
        context['feel_like'] = weather_data['feel_like']
        context['temperature'] = weather_data['temperature']
        # Polluants (PM10, PM2.5, etc.)
        air_quality_levels = pollution_data.get('air_quality_levels', {})
        context['polluants'] = [{'label': key, 'niveau': value} for key, value in air_quality_levels.items()]
        # Extraire les valeurs de chaque polluant dans le contexte
        air_quality_levels = pollution_data.get('air_quality_levels', {})
        context['PM10'] = air_quality_levels.get('PM10', 'N/A')
        context['PM25'] = air_quality_levels.get('PM2,5', 'N/A')
        context['NO2'] = air_quality_levels.get('NO2', 'N/A')
        context['O3'] = air_quality_levels.get('O3', 'N/A')
        context['SO2'] = air_quality_levels.get('SO2', 'N/A')
        # Pollens
        pollen_levels = pollen_data.get('pollen_levels', {})
        context['pollens'] = [{'label': key.capitalize(), 'niveau': value} for key, value in pollen_levels.items()]

        # Épisodes de pollution
        episodes_pollution = pollution_data.get('episodes_pollution', {})
        context['episodes_pollution'] = episodes_pollution.get('details', [])

        return context

    def get(self, request, *args, **kwargs):
        lat = request.GET.get('lat', 48.7651)
        lon = request.GET.get('lon', 2.2666)
        
        # Fetch data
        weather_data_instance = WeatherData(lat=float(lat), lon=float(lon))
        weather_data = weather_data_instance.get_weather()

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