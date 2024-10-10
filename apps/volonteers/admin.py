from django.contrib import admin
from .models import ContactForm

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'start_date', 'end_date', 'is_volunteer', 'buddy_info')
    list_filter = ('is_volunteer', 'start_date', 'end_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

    # Method to display the buddy information
    def buddy_info(self, obj):
        # Retrieve the buddy object based on the buddy_id
        try:
            buddy = ContactForm.objects.get(id=obj.buddy_id)
            return f"{buddy.first_name} {buddy.last_name} ({'Volunteer' if buddy.is_volunteer else 'Seeker'})"
        except ContactForm.DoesNotExist:
            return "No buddy assigned"

    # Customizing the column title in the admin view
    buddy_info.short_description = 'Buddy Information'

# Change the title of the admin site
admin.site.site_header = "Accès mairie"