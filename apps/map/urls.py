from django.urls import path
from .views import MapView





urlpatterns = [
    path(
        "map",
      MapView.as_view(template_name="map.html"),
        name="map",
    )
]
