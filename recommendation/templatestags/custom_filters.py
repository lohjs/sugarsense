# yourapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='replace_underscore')
def replace_underscore(value):
    if value:
        return str(value).replace('_', ' ')
    return value