from django import template
from apps.db_users.models import ContactForm

register = template.Library()

@register.filter
def get_object_from_id(buddy_id):
    """Fetch ContactForm object based on buddy_id"""
    try:
        return ContactForm.objects.get(id=buddy_id)
    except ContactForm.DoesNotExist:
        return None