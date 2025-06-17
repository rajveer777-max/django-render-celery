# core/templatetags/json_filters.py
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re
import json

register = template.Library()

@register.filter(is_safe=True, name='apply_formatting')
def apply_formatting(value):
    """
    Applies basic formatting:
    - Escapes HTML
    - Converts **text** to <strong>text</strong>
    - Converts newlines to <br>
    """
    if not isinstance(value, str):
        value = str(value)
    value = escape(value)
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    value = value.replace('\n', '<br>\n')
    return mark_safe(value)

@register.filter(name='is_dict')
def is_dict(value):
    """Checks if a value is a dictionary."""
    return isinstance(value, dict)

@register.filter(is_safe=True, name='pprint')
def pprint_json(value):
    """Pretty print Python object as JSON string for template display."""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return escape(str(value))

# --- NEW FILTER ---
@register.filter(name='replace_str')
def replace_str(value, args):
    """
    Replaces occurrences of a substring with another in a string.
    Usage: {{ some_string|replace_str:"old,new" }}
    """
    if isinstance(value, str) and isinstance(args, str):
        try:
            old, new = args.split(',')
            return value.replace(old, new)
        except ValueError:
            # Handle cases where args might not have a comma
            return value # Return original value if args format is wrong
    return value # Return original value if not a string or args format is wrong
# --- END NEW FILTER ---

# Keep the get_item filter if you chose Option 2 previously, otherwise optional
# @register.filter(name='get_item')
# def get_item(dictionary, key):
#    return dictionary.get(key)