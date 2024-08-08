from django import template

register = template.Library()

@register.simple_tag
def toggle_order(current_order):
    return 'desc' if current_order == 'asc' else 'asc'
