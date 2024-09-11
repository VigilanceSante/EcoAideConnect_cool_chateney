from django.urls import path
from .views import FormLayoutsView



urlpatterns = [
    path(
        "form/layouts_vertical/",
        FormLayoutsView.as_view(template_name="contact_form.html"),
        name="contact_form",
    )
]
