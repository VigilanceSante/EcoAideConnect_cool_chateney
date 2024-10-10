from django.urls import path
from .views import BuddiesDashboardView



urlpatterns = [
    path(
        "twosome/",
      BuddiesDashboardView.as_view(template_name="twosome.html"),
        name="twosome",
    )
]
