"""
This module contains the URL configuration for the authentication app.
"""
from django.urls import path
from .views import InviteUserView, RegisterView, LoginView


urlpatterns = [
    path(
        "auth/login/",
        LoginView.as_view(template_name="auth_login_basic.html"),
        name="login",
    ),
    path(
        "auth/register/<str:token>/",
        RegisterView.as_view(template_name="auth_register_basic.html"),
        name="register",
    ),
    path(
        "auth/forgot_password/",
        RegisterView.as_view(template_name="auth_forgot_password_basic.html"),
        name="password-reset",
    ),
    path(
        "auth/invitation/",
        InviteUserView.as_view(template_name="auth_invitation_for_registration.html"),
        name="invitation",
    )
]
