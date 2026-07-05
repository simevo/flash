from django import template

register = template.Library()


@register.filter(name="get_image")
def get_image(value, feed_id):
    return value[feed_id].image or "/static/images/unknown.png"
