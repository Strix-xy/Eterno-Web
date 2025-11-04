"""
ETERNO E-Commerce Platform - PDF Receipt Generator
Generates PDF receipts for sales and orders
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import json
from app.models import Product

def generate_sale_receipt(sale):
    """
    Generate PDF receipt for POS sale
    
    Args:
        sale: Sale model instance
    
    Returns:
        BytesIO buffer containing PDF data
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Receipt header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(220, 750, "ETERNO")
    p.setFont("Helvetica", 10)
    p.drawString(200, 730, "Timeless Fashion - Receipt")
    p.line(50, 720, 550, 720)
    
    # Sale information
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Sale ID: {sale.id}")
    p.drawString(50, 680, f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(50, 660, f"Payment: {sale.payment_method.upper()}")
    p.line(50, 650, 550, 650)
    
    # Items table header
    items = json.loads(sale.items)
    y_position = 630
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Item")
    p.drawString(300, y_position, "Qty")
    p.drawString(380, y_position, "Price")
    p.drawString(480, y_position, "Total")
    
    y_position -= 20
    p.setFont("Helvetica", 10)
    
    # List all items
    for item in items:
        product = Product.query.get(item['product_id'])
        if product:
            # Truncate long names
            name = product.name[:35]
            p.drawString(50, y_position, name)
            p.drawString(300, y_position, str(item['quantity']))
            p.drawString(380, y_position, f"₱{product.price:.2f}")
            p.drawString(480, y_position, f"₱{product.price * item['quantity']:.2f}")
            y_position -= 20
            
            # Check if we need a new page
            if y_position < 100:
                p.showPage()
                y_position = 750
    
    # Discount and total
    p.line(50, y_position, 550, y_position)
    y_position -= 20
    
    if sale.discount_amount > 0:
        p.setFont("Helvetica", 10)
        p.drawString(380, y_position, f"Discount ({sale.discount_type}):")
        p.drawString(480, y_position, f"-₱{sale.discount_amount:.2f}")
        y_position -= 20
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(380, y_position, "TOTAL:")
    p.drawString(480, y_position, f"₱{sale.total_amount:.2f}")
    
    # Footer
    y_position -= 40
    p.setFont("Helvetica", 8)
    p.drawCentredString(300, y_position, "Thank you for your purchase!")
    p.drawCentredString(300, y_position - 15, "ETERNO - Timeless Fashion")
    
    p.save()
    buffer.seek(0)
    return buffer

def generate_order_receipt(order):
    """
    Generate PDF receipt for customer order
    
    Args:
        order: Order model instance
    
    Returns:
        BytesIO buffer containing PDF data
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Receipt header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(220, 750, "ETERNO")
    p.setFont("Helvetica", 10)
    p.drawString(200, 730, "Timeless Fashion - Order Receipt")
    p.line(50, 720, 550, 720)
    
    # Order information
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Order ID: {order.id}")
    p.drawString(50, 680, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(50, 660, f"Customer: {order.customer_name}")
    p.drawString(50, 640, f"Email: {order.customer_email}")
    p.drawString(50, 620, f"Payment: {order.payment_method.upper()}")
    p.drawString(50, 600, f"Status: {order.status.upper()}")
    
    y_start = 580
    if order.customer_address:
        p.setFont("Helvetica", 10)
        p.drawString(50, y_start, f"Address: {order.customer_address[:60]}")
        y_start -= 20
    
    p.line(50, y_start, 550, y_start)
    
    # Items table header
    items = json.loads(order.items)
    y_position = y_start - 20
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Item")
    p.drawString(300, y_position, "Qty")
    p.drawString(380, y_position, "Price")
    p.drawString(480, y_position, "Total")
    
    y_position -= 20
    p.setFont("Helvetica", 10)
    
    # List all items
    for item in items:
        name = item['product_name'][:35]
        p.drawString(50, y_position, name)
        p.drawString(300, y_position, str(item['quantity']))
        p.drawString(380, y_position, f"₱{item['price']:.2f}")
        p.drawString(480, y_position, f"₱{item['price'] * item['quantity']:.2f}")
        y_position -= 20
        
        # Check if we need a new page
        if y_position < 150:
            p.showPage()
            y_position = 750
    
    # Totals
    p.line(50, y_position, 550, y_position)
    y_position -= 20
    
    p.setFont("Helvetica", 10)
    p.drawString(380, y_position, "Subtotal:")
    p.drawString(480, y_position, f"₱{order.subtotal:.2f}")
    y_position -= 20
    
    p.drawString(380, y_position, "Shipping:")
    p.drawString(480, y_position, f"₱{order.shipping_fee:.2f}")
    y_position -= 20
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(380, y_position, "TOTAL:")
    p.drawString(480, y_position, f"₱{order.total_amount:.2f}")
    
    # Footer
    y_position -= 40
    p.setFont("Helvetica", 8)
    p.drawCentredString(300, y_position, "Thank you for shopping with us!")
    p.drawCentredString(300, y_position - 15, "ETERNO - Timeless Fashion")
    
    p.save()
    buffer.seek(0)
    return buffer