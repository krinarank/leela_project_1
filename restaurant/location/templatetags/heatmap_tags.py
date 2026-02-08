from django import template

register = template.Library()

@register.filter
def heat_color(order_count):
    """
    Converts order count into a gradient color from blue -> yellow -> red
    """
    count = int(order_count)
    if count <= 5:
        return '#3498db'  # blue
    elif count <= 15:
        return '#f1c40f'  # yellow
    else:
        return '#e74c3c'  # red
