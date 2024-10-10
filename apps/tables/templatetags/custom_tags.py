# apps/tables/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.simple_tag
def toggle_order(current_order):
    """Toggle between ascending and descending order."""
    return 'desc' if current_order == 'asc' else 'asc'