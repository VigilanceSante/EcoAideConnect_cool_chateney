# apps/dashboard_volonteers/templatetags/availability_tags.py
from django import template
from django.utils.dateparse import parse_date
from apps.volontaires.models import ContactForm

register = template.Library()

@register.filter(name='filter_by_date_range')
def filter_by_date_range(queryset, date_range):
    """
    Filter the queryset based on the provided date range.
    `date_range` should be a tuple (start_date, end_date) or (start_date,).
    """
    if not date_range:
        return queryset

    start_date, end_date = date_range

    if start_date and end_date:
        queryset = queryset.filter(start_date__gte=parse_date(start_date), end_date__lte=parse_date(end_date))
    elif start_date:
        queryset = queryset.filter(start_date__gte=parse_date(start_date))
    elif end_date:
        queryset = queryset.filter(end_date__lte=parse_date(end_date))

    return queryset
