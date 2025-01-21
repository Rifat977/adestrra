from django import template
from django.utils.html import strip_tags


register = template.Library()

@register.filter
def dict_key(value, key):
    return value.get(key, None)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def truncate_html(value, limit=150):

    if not isinstance(value, str):
        return value

    plain_text = strip_tags(value)

    if len(plain_text) > limit:
        return f"{plain_text[:limit].rstrip()}..."
    return plain_text