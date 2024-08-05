from django.contrib import admin
from .models import ContactForm  # Adjust to your model names

@admin.register(ContactForm)  # Use the decorator or register directly
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')  # Customize as needed