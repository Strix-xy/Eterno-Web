"""
ETERNO E-Commerce Platform - Helper Functions
Utility functions used across the application
"""
import re
import random
from flask import current_app

def format_peso(amount):
    """
    Format amount as Philippine Peso with proper formatting
    
    Args:
        amount: Numeric amount to format (can be None)
    
    Returns:
        Formatted string with peso symbol (e.g., "₱1,234.56")
    """
    if amount is None:
        return "₱0.00"
    try:
        return f"₱{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "₱0.00"


def is_valid_email(email):
    """
    Validate email format using regex pattern
    
    Args:
        email: Email string to validate
    
    Returns:
        Boolean indicating if email is valid
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def calculate_shipping_fee(has_address=False):
    """
    Calculate randomized shipping fee if address is provided
    Uses configuration values for min/max range
    
    Args:
        has_address: Boolean indicating if shipping address is provided
    
    Returns:
        Shipping fee amount (0 if no address, random between min-max otherwise)
    """
    if not has_address:
        return 0
    
    # Get shipping fee range from config or use defaults
    min_fee = current_app.config.get('SHIPPING_FEE_MIN', 50)
    max_fee = current_app.config.get('SHIPPING_FEE_MAX', 200)
    
    return random.randint(min_fee, max_fee)


def calculate_discount(subtotal, discount_type):
    """
    Calculate discount amount based on discount type
    
    Args:
        subtotal: Order subtotal amount
        discount_type: Type of discount ('pwd', 'senior', 'voucher', or 'none')
    
    Returns:
        Discount amount (0 if invalid type or subtotal)
    """
    if not subtotal or subtotal <= 0:
        return 0
    
    if not discount_type or discount_type == 'none':
        return 0
    
    # PWD and Senior Citizen discount (20% by default)
    if discount_type in ['pwd', 'senior']:
        discount_rate = current_app.config.get('PWD_SENIOR_DISCOUNT', 0.20)
        return float(subtotal) * discount_rate
    
    # Fixed voucher discount (₱100 by default)
    elif discount_type == 'voucher':
        return float(current_app.config.get('VOUCHER_DISCOUNT', 100))
    
    return 0


def validate_product_data(data):
    """
    Validate product data for add/update operations
    
    Args:
        data: Dictionary containing product data
    
    Returns:
        Tuple (is_valid, error_message)
    """
    # Check required fields
    if not data.get('name') or not data.get('name').strip():
        return False, "Product name is required"
    
    # Validate price
    try:
        price = float(data.get('price', 0))
        if price < 0:
            return False, "Price must be non-negative"
    except (ValueError, TypeError):
        return False, "Invalid price value"
    
    # Validate stock
    try:
        stock = int(data.get('stock', 0))
        if stock < 0:
            return False, "Stock must be non-negative"
    except (ValueError, TypeError):
        return False, "Invalid stock value"
    
    return True, None


def sanitize_string(value, max_length=None):
    """
    Sanitize string input by stripping whitespace and limiting length
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length (optional)
    
    Returns:
        Sanitized string
    """
    if not value or not isinstance(value, str):
        return ""
    
    sanitized = value.strip()
    
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def calculate_cart_totals(cart_items):
    """
    Calculate subtotal and item count for cart
    
    Args:
        cart_items: List of tuples (Cart, Product)
    
    Returns:
        Dictionary with 'subtotal' and 'item_count'
    """
    subtotal = 0
    item_count = 0
    
    for cart_item, product in cart_items:
        if product and cart_item.quantity > 0:
            subtotal += product.price * cart_item.quantity
            item_count += cart_item.quantity
    
    return {
        'subtotal': subtotal,
        'item_count': item_count
    }


def validate_payment_method(payment_method):
    """
    Validate payment method
    
    Args:
        payment_method: Payment method string
    
    Returns:
        Boolean indicating if payment method is valid
    """
    valid_methods = ['cash', 'cod', 'gcash', 'bank_transfer']
    return payment_method in valid_methods if payment_method else False


def validate_order_status(status):
    """
    Validate order status
    
    Args:
        status: Order status string
    
    Returns:
        Boolean indicating if status is valid
    """
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'completed']
    return status in valid_statuses if status else False