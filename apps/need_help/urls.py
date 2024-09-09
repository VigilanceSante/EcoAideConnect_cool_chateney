from django.urls import path
from .views import FormLayoutsHelp



urlpatterns = [
    path(
        "need_help/",
        FormLayoutsHelp.as_view(template_name="help.html"),
        name="help",
    )
]
