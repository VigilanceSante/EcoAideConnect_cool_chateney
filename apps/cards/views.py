from django.views.generic import TemplateView
from apps.modules.streaming import WeatherData, RecosanteAPI
from web_project import TemplateLayout

class CombinedData(TemplateView):
    template_name = 'air_quality_dashboard.html'

    def map_pollution_level(self, level):
        """Convertir les niveaux de pollution en valeurs numériques pour les jauges."""
        if level == 'Bon':
            return 25
        elif level == 'Moyen':
            return 50
        elif level == 'Mauvais':
            return 75
        elif level == 'Très Mauvais':
            return 100
        return 0  # Valeur par défaut si aucune correspondance

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Récupération des données météo, pollution et pollen
        weather_data = kwargs.get('weather_data', {})
        pollution_data = kwargs.get('pollution_data', {})
        pollen_data = kwargs.get('pollen_data', {})

        # Météo
        context['temperature'] = weather_data.get('temperature', 'N/A')
        context['feel_like'] = weather_data.get('feel_like', 'N/A')
        context['wind_speed'] = weather_data.get('wind_speed', 'N/A')
        context['min_temp'] = weather_data.get('min_temp', 'N/A')
        context['max_temp'] = weather_data.get('max_temp', 'N/A')

        # Pollution (convertir les niveaux en valeurs numériques pour les jauges et les afficher textuellement)
        air_quality_levels = pollution_data.get('air_quality_levels', {})
        context['PM10_value'] = self.map_pollution_level(air_quality_levels.get('PM10', 'N/A'))
        context['PM10_text'] = air_quality_levels.get('PM10', 'N/A')
        context['PM25_value'] = self.map_pollution_level(air_quality_levels.get('PM2,5', 'N/A'))
        context['PM25_text'] = air_quality_levels.get('PM2,5', 'N/A')
        context['NO2_value'] = self.map_pollution_level(air_quality_levels.get('NO2', 'N/A'))
        context['NO2_text'] = air_quality_levels.get('NO2', 'N/A')
        context['O3_value'] = self.map_pollution_level(air_quality_levels.get('O3', 'N/A'))
        context['O3_text'] = air_quality_levels.get('O3', 'N/A')
        context['SO2_value'] = self.map_pollution_level(air_quality_levels.get('SO2', 'N/A'))
        context['SO2_text'] = air_quality_levels.get('SO2', 'N/A')

        # Pollens
        pollen_levels = pollen_data.get('pollen_levels', {})
        context['pollens'] = [{'label': key.capitalize(), 'niveau': value} for key, value in pollen_levels.items()]

        return context

    def get(self, request, *args, **kwargs):
        lat = request.GET.get('lat', 48.7651)
        lon = request.GET.get('lon', 2.2666)

        # Fetch des données météo via OpenWeather
        weather_data_instance = WeatherData(lat=float(lat), lon=float(lon))
        weather_data = weather_data_instance.get_weather()

        # Fetch des données de RecoSanté
        recosante_api = RecosanteAPI()
        recosante_data = recosante_api.fetch_data()

        # Extraction des données pollution et pollen
        pollution_data = recosante_data.get('indice_atmo', {})
        pollen_data = recosante_data.get('raep', {})

        # Préparation du contexte avec les données
        context = self.get_context_data(
            weather_data=weather_data,
            pollution_data=pollution_data,
            pollen_data=pollen_data
        )

        return self.render_to_response(context)