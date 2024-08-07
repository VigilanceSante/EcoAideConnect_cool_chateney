from django import template

register = template.Library()

@register.simple_tag
def availability_fields():
    return [
        'monday_all_day', 'monday_morning', 'monday_afternoon', 'monday_evening',
        'tuesday_all_day', 'tuesday_morning', 'tuesday_afternoon', 'tuesday_evening',
        'wednesday_all_day', 'wednesday_morning', 'wednesday_afternoon', 'wednesday_evening',
        'thursday_all_day', 'thursday_morning', 'thursday_afternoon', 'thursday_evening',
        'friday_all_day', 'friday_morning', 'friday_afternoon', 'friday_evening',
        'saturday_all_day', 'saturday_morning', 'saturday_afternoon', 'saturday_evening',
        'sunday_all_day', 'sunday_morning', 'sunday_afternoon', 'sunday_evening',
    ]

@register.filter
def replace_underscore(value):
    return value.replace('_', ' ').capitalize()
