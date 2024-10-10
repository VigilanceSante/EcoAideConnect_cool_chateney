from django import template

register = template.Library()

@register.filter
def dict_value(contact, field_name):
    return getattr(contact, field_name, None)