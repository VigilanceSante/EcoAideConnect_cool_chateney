# apps/form_layouts/admin.py
from django.contrib import admin
from .models import ContactForm

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

# admin.site.register(ContactForm, ContactFormAdmin)  # alternative way
# change the title of the admin site
admin.site.site_header = "Accés mairie"
