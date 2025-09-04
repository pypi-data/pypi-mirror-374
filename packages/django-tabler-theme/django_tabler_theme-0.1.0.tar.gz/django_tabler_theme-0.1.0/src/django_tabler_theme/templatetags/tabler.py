from django import template
from django.urls import resolve

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_active(context, *url_names):
    """Return 'active' if current view's url_name is in url_names."""
    try:
        current = resolve(context["request"].path_info).url_name
    except Exception:
        return ""
    return "active" if current in url_names else ""


@register.filter
def add_class(field, css):
    return field.as_widget(attrs={**(field.field.widget.attrs or {}), "class": css})
