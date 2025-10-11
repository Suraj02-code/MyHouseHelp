from django import template

register = template.Library()


def _format_indian_number(value: float) -> str:
    """Format a number using Indian numbering system (lakh/crore)."""
    # Ensure we work with a string version having two decimals
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0.00"

    is_negative = number < 0
    number = abs(number)

    integer_part = int(number)
    decimal_part = f"{number:.2f}".split(".")[1]

    s = str(integer_part)
    if len(s) <= 3:
        grouped = s
    else:
        # Last 3 digits remain together, preceding digits grouped by 2
        last3 = s[-3:]
        rest = s[:-3]
        pairs = []
        while len(rest) > 2:
            pairs.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            pairs.insert(0, rest)
        grouped = ",".join(pairs + [last3])

    sign = "-" if is_negative else ""
    return f"{sign}{grouped}.{decimal_part}"


@register.filter(name="inr")
def inr(value):
    """Return a value formatted as Indian Rupees, prefixed with the rupee symbol.

    Usage in templates: {{ amount|inr }} -> ₹12,34,567.89
    """
    formatted = _format_indian_number(value)
    return f"₹{formatted}"


