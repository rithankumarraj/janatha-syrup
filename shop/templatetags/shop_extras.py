from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply two values: {{ price|multiply:quantity }}"""
    try:
        return float(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def currency(value):
    """Format as Indian Rupees: {{ price|currency }}"""
    try:
        return f'₹{float(value):,.2f}'
    except (ValueError, TypeError):
        return '₹0.00'


@register.filter
def star_range(value):
    """Return range for star ratings: {% for i in rating|star_range %}"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def empty_star_range(value):
    """Return range for empty stars: {% for i in rating|empty_star_range %}"""
    try:
        return range(5 - int(value))
    except (ValueError, TypeError):
        return range(5)
