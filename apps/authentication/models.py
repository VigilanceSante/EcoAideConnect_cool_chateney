from django.utils.crypto import get_random_string
from django.db import models
from django.contrib.auth.models import User

def generate_token():
    return get_random_string(64)

class RegisterInvitation(models.Model):
    """
    A model to store the invitation to register.
    """
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=64, default='town_hall_employee')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure the token is generated only if not already set
        if not self.token:
            self.token = generate_token()
        super().save(*args, **kwargs)
