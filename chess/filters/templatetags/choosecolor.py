from django import template

register = template.Library()

@register.filter
def choosecolor(row, col):
    result = "sq-b"
    if (int(row) + int(col)) % 2 == 0:
        result = "sq-w"
    return result
