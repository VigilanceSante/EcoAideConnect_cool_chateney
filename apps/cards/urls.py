from django.urls import path
from .views import CombinedData



urlpatterns = [
    path(
        "cards/basic/",
      CombinedData.as_view(template_name="dash.html"),
        name="dash",
    )
]
