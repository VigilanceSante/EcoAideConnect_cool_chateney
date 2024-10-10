from django.views.generic import TemplateView
from web_project import TemplateLayout


class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['default_location'] = [48.765, 2.266]  # Châtenay-Malabry coordinates
        context['default_location_name'] = "Châtenay-Malabry"
        return context
