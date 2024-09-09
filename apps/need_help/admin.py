# apps/form_layouts/admin.py
from django.contrib import admin
from .models import HelpRequest

@admin.register(HelpRequest)

class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')

# admin.site.register(ContactForm, ContactFormAdmin)  # alternative way
# change the title of the admin site
admin.site.site_header = "Accés mairie"
