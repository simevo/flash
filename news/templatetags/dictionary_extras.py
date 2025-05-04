from django import template

register = template.Library()


@register.filter(name="get_image")
def get_image(value, arg):
    return value[arg].image
