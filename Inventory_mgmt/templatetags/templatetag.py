from django import template


register = template.Library()
@register.filter(name='get_name')
def get_name(dictionary, key):
    return dictionary[key]['name']

@register.filter(name='get_width')
def get_width(dictionary, key):
    return dictionary[key]['width']

@register.filter(name='get_height')
def get_height(dictionary, key):
    return dictionary[key]['height']