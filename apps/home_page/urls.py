from django.urls import path
from .views import CombinedData



urlpatterns = [
    path(
        "",
        CombinedData.as_view(template_name="home_page.html"),
        name="index",
    )
]
