"""
This module contains the URL configuration for the authentication app.
"""
from django.urls import path
from .views import RegisterView, LoginView


urlpatterns = [
    path(
        "auth/login/",
        LoginView.as_view(template_name="auth_login_basic.html"),
        name="login",
    ),
    path(
        "auth/register/",
        RegisterView.as_view(template_name="auth_register_basic.html"),
        name="register",
    ),
    path(
        "auth/forgot_password/",
        RegisterView.as_view(template_name="auth_forgot_password_basic.html"),
        name="password-reset",
    ),
]
