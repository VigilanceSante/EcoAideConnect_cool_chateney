from django.urls import path
from .views import CombinedData



urlpatterns = [
    path(
        "forcast/",
      CombinedData.as_view(template_name="forcast.html"),
        name="forcast",
    )
]
