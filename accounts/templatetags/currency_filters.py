from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def pkr_currency(value):
    """
    Format currency values in Pakistani Rupees format.
    Usage: {{ amount|pkr_currency }}
    """
    if value is None:
        return "Rs. 0.00"
    
    try:
        # Convert to Decimal for precise formatting
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Format with 2 decimal places
        formatted_value = f"{value:.2f}"
        return f"Rs. {formatted_value}"
    except:
        return "Rs. 0.00"

@register.filter  
def pkr_short(value):
    """
    Format currency values in short Pakistani Rupees format (no decimal places for whole numbers).
    Usage: {{ amount|pkr_short }}
    """
    if value is None:
        return "Rs. 0"
    
    try:
        # Convert to Decimal for precise formatting
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Show decimals only if not a whole number
        if value % 1 == 0:
            return f"Rs. {int(value)}"
        else:
            return f"Rs. {value:.2f}"
    except:
        return "Rs. 0"