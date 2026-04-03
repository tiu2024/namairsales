from django import template

register = template.Library()


@register.filter
def uzs(value):
    """Format a number with space thousands separator, e.g. 12450000 → 12 450 000."""
    try:
        return f"{int(value):,}".replace(",", "\u00a0")
    except (ValueError, TypeError):
        return value


@register.filter
def usd(value):
    """Format a number as USD with comma thousands separator, e.g. 1250.5 → 1,250.50"""
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def absval(value):
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value
