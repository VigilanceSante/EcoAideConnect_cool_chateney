from django.urls import path
from .views import CardView



urlpatterns = [
    path(
        "cards/basic/",
      CardView.as_view(template_name="dash.html"),
        name="dash",
    )
]
