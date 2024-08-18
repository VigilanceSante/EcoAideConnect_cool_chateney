from django.apps import AppConfig

# This module defines the configuration for the authentication app.


class AuthenticationConfig(AppConfig):
    """
    Configuration class for the authentication app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
