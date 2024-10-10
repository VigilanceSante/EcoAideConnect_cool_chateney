from django.contrib import admin
from .models import ContactForm

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'email', 
        'phone', 'start_date', 'end_date', 
        'is_volunteer', 'buddy_info', 
        'available_days'  # Include availability days
    )
    list_filter = ('is_volunteer', 'start_date', 'end_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

    # Read-only fields
    readonly_fields = ('buddy_info',)

    # Method to display the buddy information
    def buddy_info(self, obj):
        if obj.buddy_id:  # Check if a buddy is assigned
            try:
                buddy = ContactForm.objects.get(id=obj.buddy_id)
                return f"{buddy.first_name} {buddy.last_name} ({'Volunteer' if buddy.is_volunteer else 'Seeker'})"
            except ContactForm.DoesNotExist:
                return "No buddy assigned"
        return "No buddy assigned"

    buddy_info.short_description = 'Buddy Information'

    # Method to display available days
    def available_days(self, obj):
        days = []
        # Check availability for each day and time slot
        if obj.monday_all_day:
            days.append("Lundi toute la journée")
        if obj.monday_morning:
            days.append("Lundi matin")
        if obj.monday_afternoon:
            days.append("Lundi après-midi")
        if obj.monday_evening:
            days.append("Lundi soir")

        if obj.tuesday_all_day:
            days.append("Mardi toute la journée")
        if obj.tuesday_morning:
            days.append("Mardi matin")
        if obj.tuesday_afternoon:
            days.append("Mardi après-midi")
        if obj.tuesday_evening:
            days.append("Mardi soir")

        if obj.wednesday_all_day:
            days.append("Mercredi toute la journée")
        if obj.wednesday_morning:
            days.append("Mercredi matin")
        if obj.wednesday_afternoon:
            days.append("Mercredi après-midi")
        if obj.wednesday_evening:
            days.append("Mercredi soir")

        if obj.thursday_all_day:
            days.append("Jeudi toute la journée")
        if obj.thursday_morning:
            days.append("Jeudi matin")
        if obj.thursday_afternoon:
            days.append("Jeudi après-midi")
        if obj.thursday_evening:
            days.append("Jeudi soir")

        if obj.friday_all_day:
            days.append("Vendredi toute la journée")
        if obj.friday_morning:
            days.append("Vendredi matin")
        if obj.friday_afternoon:
            days.append("Vendredi après-midi")
        if obj.friday_evening:
            days.append("Vendredi soir")

        if obj.saturday_all_day:
            days.append("Samedi toute la journée")
        if obj.saturday_morning:
            days.append("Samedi matin")
        if obj.saturday_afternoon:
            days.append("Samedi après-midi")
        if obj.saturday_evening:
            days.append("Samedi soir")

        if obj.sunday_all_day:
            days.append("Dimanche toute la journée")
        if obj.sunday_morning:
            days.append("Dimanche matin")
        if obj.sunday_afternoon:
            days.append("Dimanche après-midi")
        if obj.sunday_evening:
            days.append("Dimanche soir")

        return ", ".join(days) if days else "Aucune disponibilité"

    available_days.short_description = 'Jours Disponibles'  # Custom column title

    # Fieldsets to group fields logically (optional)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Availability', {
            'fields': (
                'start_date', 'end_date', 'is_volunteer', 
                'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
                'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
                'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
                'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
                'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
                'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
                'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening'
            ),
            'classes': ('collapse',)  # Make this section collapsible
        }),
        ('Buddy Information', {
            'fields': ('buddy_info',),
            'classes': ('collapse',)  # Make this section collapsible
        }),
    )

# Change the title of the admin site
admin.site.site_header = "Accès mairie"
admin.site.site_title = "Admin - Accès mairie"
admin.site.index_title = "Administration"