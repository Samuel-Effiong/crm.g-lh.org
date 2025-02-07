import os
import json
import string

from datetime import datetime, time

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
@stringfilter
def empty_space_if_none(value: str) -> str:
    value = value.lower().strip()
    if value == 'none' or value == '-':
        return ""
    return value.strip()


@register.filter()
@stringfilter
def my_date_filter(value: str) -> str:
    if value == 'None':
        return ""
    else:
        date = datetime.strptime(value, "%Y-%m-%d")
        return date.strftime('%a, %d %B, %Y')


@register.filter()
@stringfilter
def my_time_filter(value: str) -> str:
    my_time = time.fromisoformat(value)

    return str(my_time)


@register.filter()
@stringfilter
def format_text(value: str) -> str:
    if value == 'nan':
        return ""
    elif '_' in value:
        text = value.split('_')
        if len(text) <= 2:
            return " ".join(text).title()
        elif len(text) > 2:
            return "/".join(text[:2]).title() + f" {text[-1]}".title()
    else:
        return value


@register.simple_tag()
def calculate_percentage(value, total):
    try:
        return round((value * 100) / total)
    except ZeroDivisionError:
        return 0


@register.filter()
def remove_special_punctuation(value: str):
    if '/' in value:
        new_value = value.replace('/', '__and__')
    else:
        new_value = value

    return new_value


@register.simple_tag()
def special_dictionary_formatter(dict_, key, inner_key=None):
    if inner_key is None:
        result = dict_[key]
    else:
        result = dict_[key]
        try:
            result = result[inner_key]
        except KeyError:
            return "Key Error"
    return result


@register.filter()
def add_1000(value: int) -> int:
    """Add 1000 to the value to be able to create unique ids that do not clash"""
    return value + 1000


@register.filter(is_safe=True)
def jsonify(json_object):
    """
    Output the json encoding of its argument.
    This will escape all the HTML/XML special characters with their unicode
    escapes, so it is safe to be output anywhere except for inside a tag
    attribute.
    If the output needs to be put in an attribute, entitize the output of this
    filter.
    """

    json_str = json.dumps(json_object)

    # Escape all the XML/HTML special characters.
    escapes = ["<", ">", "&"]
    for c in escapes:
        json_str = json_str.replace(c, r"\u%04x" % ord(c))

    # now it's safe to use mark_safe
    return mark_safe(json_str)


@register.filter()
def length(value) -> int:
    return len(value)


@register.filter()
def concatenate(value, arg) -> str:
    return f"{value} {arg}"


@register.simple_tag()
def get_range(value):
    return range(value)