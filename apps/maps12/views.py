from django.views.generic import TemplateView

class MapView(TemplateView):
    template_name = 'maps.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_location'] = [48.765, 2.266]  # Châtenay-Malabry coordinates
        context['default_location_name'] = "Châtenay-Malabry"
        return context
