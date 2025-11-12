"""
ETERNO E-Commerce Platform - Customer Routes
Handles customer shopping, cart, and checkout functionality
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file
from app import db
from app.models import Product, Cart, Order, User
from app.utils.helpers import (
    calculate_shipping_fee, calculate_cart_totals,
    validate_payment_method, sanitize_string
)
from app.utils.export import export_to_excel
from app.utils.pdf import generate_order_receipt
import json

customer_bp = Blueprint('customer', __name__)

# ==================== SHOP ====================

@customer_bp.route('/shop')
def shop():
    """Customer shop page - display all available products"""
    # Get only products with stock
    products = Product.query.filter(Product.stock > 0).order_by(Product.name).all()
    
    return render_template('shop.html', products=products)


@customer_bp.route('/about')
def about():
    """About page - brand story and values"""
    return render_template('about.html')


# ==================== SHOPPING CART ====================

@customer_bp.route('/cart')
def cart():
    """Shopping cart page - view items before checkout"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get cart items with product details
    cart_items = db.session.query(Cart, Product).join(Product).filter(
        Cart.user_id == session['user_id']
    ).all()
    
    # Calculate total subtotal
    total_subtotal = sum(product.price * cart_item.quantity for cart_item, product in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_subtotal=total_subtotal)


@customer_bp.route('/cart/count')
def cart_count():
    """API endpoint to get total items in cart (for navbar badge)"""
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    # Sum all quantities in cart
    count = db.session.query(db.func.sum(Cart.quantity)).filter(
        Cart.user_id == session['user_id']
    ).scalar() or 0
    
    return jsonify({'count': int(count)})


@customer_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add product to shopping cart"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    try:
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Validate input
        if not product_id:
            return jsonify({'error': 'Product ID required'}), 400
        
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        # Check if product exists and has stock
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if not product.is_in_stock(quantity):
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Check if item already in cart
        cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if cart_item:
            # Increase quantity
            new_quantity = cart_item.quantity + quantity
            if not product.is_in_stock(new_quantity):
                return jsonify({'error': 'Insufficient stock'}), 400
            cart_item.quantity = new_quantity
        else:
            # Add new cart item
            cart_item = Cart(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        # Return updated cart count
        cart_count = db.session.query(db.func.sum(Cart.quantity)).filter(
            Cart.user_id == session['user_id']
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'cart_count': int(cart_count)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add to cart'}), 500


@customer_bp.route('/cart/update/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    """Update cart item quantity"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        cart_item = Cart.query.get_or_404(cart_id)
        
        # Verify cart item belongs to user
        if cart_item.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        change = data.get('change', 0)
        new_quantity = cart_item.quantity + change
        
        # Remove item if quantity reaches 0 or below
        if new_quantity <= 0:
            db.session.delete(cart_item)
        else:
            # Check stock availability
            if not cart_item.product.is_in_stock(new_quantity):
                return jsonify({'error': 'Insufficient stock'}), 400
            cart_item.quantity = new_quantity
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update cart'}), 500


@customer_bp.route('/cart/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """Remove item from cart"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        cart_item = Cart.query.get_or_404(cart_id)
        
        # Verify cart item belongs to user
        if cart_item.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove item'}), 500


# ==================== CHECKOUT ====================

@customer_bp.route('/checkout', methods=['POST'])
def checkout():
    """Process customer checkout with shipping details"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    try:
        data = request.json
        payment_method = data.get('payment_method')
        customer_address = sanitize_string(data.get('customer_address', ''))
        voucher_applied = data.get('voucher_applied', False)
        delivery_fee = data.get('delivery_fee', 0)

        # Require delivery address for all payment methods
        if not customer_address:
            return jsonify({'error': 'Delivery address is required for checkout'}), 400
        
        # Validate payment method
        valid_methods = ['cod', 'gcash', 'credit_card', 'paypal']
        if payment_method not in valid_methods:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        # Validate payment-specific fields
        if payment_method == 'cod' and not customer_address:
            return jsonify({'error': 'Delivery address is required for COD'}), 400
        elif payment_method == 'gcash' and not data.get('gcash_number'):
            return jsonify({'error': 'GCash number is required'}), 400
        elif payment_method == 'credit_card':
            if not data.get('card_number') or not data.get('card_expiry') or not data.get('card_cvv'):
                return jsonify({'error': 'All card details are required'}), 400
        elif payment_method == 'paypal':
            if not data.get('paypal_email') or not data.get('paypal_name'):
                return jsonify({'error': 'PayPal email and name are required'}), 400
        
        # Get user information
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get cart items
        cart_items = db.session.query(Cart, Product).join(Product).filter(
            Cart.user_id == session['user_id']
        ).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Calculate subtotal
        cart_data = calculate_cart_totals(cart_items)
        subtotal = cart_data['subtotal']
        
        # Apply voucher discount if applicable
        discount_amount = 0
        if voucher_applied:
            discount_amount = 100  # Fixed ₱100 voucher discount
            subtotal = max(0, subtotal - discount_amount)
        
        # Use provided delivery fee or calculate random one (min ₱50, max ₱100)
        import random
        if not delivery_fee or delivery_fee < 50:
            delivery_fee = random.randint(50, 100)  # Random between 50-100
        
        total_amount = subtotal + delivery_fee
        
        # Validate stock and prepare order items
        order_items = []
        for cart_item, product in cart_items:
            if not product.is_in_stock(cart_item.quantity):
                return jsonify({
                    'error': f'Insufficient stock for {product.name}. Available: {product.stock}'
                }), 400
            
            # Reduce stock
            product.reduce_stock(cart_item.quantity)
            
            order_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': cart_item.quantity,
                'price': product.price
            })
        
        # Create order record
        new_order = Order(
            user_id=session['user_id'],
            customer_name=user.username,
            customer_email=user.email,
            customer_address=customer_address,
            subtotal=subtotal + discount_amount,  # Store original subtotal before discount
            shipping_fee=delivery_fee,
            total_amount=total_amount,
            payment_method=payment_method,
            items=json.dumps(order_items),
            status='completed' if payment_method == 'cod' else 'pending'
        )
        
        db.session.add(new_order)
        
        # Clear user's cart
        Cart.query.filter_by(user_id=session['user_id']).delete()
        
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({
            'success': True,
            'order_id': new_order.id,
            'payment_method': payment_method,
            'shipping_fee': delivery_fee,
            'total_amount': total_amount
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Checkout failed. Please try again.'}), 500


@customer_bp.route('/receipt/<int:order_id>')
def customer_receipt(order_id):
    """Generate PDF receipt for customer order"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    order = Order.query.get_or_404(order_id)
    
    # Verify order belongs to user
    if order.user_id != session['user_id']:
        return redirect(url_for('customer.shop'))
    
    buffer = generate_order_receipt(order)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'order_{order_id}.pdf',
        mimetype='application/pdf'
    )