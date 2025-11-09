"""
ETERNO E-Commerce Platform - Admin Routes
Handles admin dashboard, POS, inventory management, and sales
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file
from app import db
from app.models import User, Product, Sale, Order
from app.utils.helpers import (
    calculate_discount, validate_product_data, 
    sanitize_string, validate_payment_method
)
from app.utils.export import export_to_excel
from app.utils.pdf import generate_sale_receipt
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard - display real-time statistics"""
    # Check admin authorization
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Calculate statistics
    total_products = Product.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    
    # Calculate total revenue from both POS sales and customer orders
    pos_revenue = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
    order_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_revenue = pos_revenue + order_revenue
    
    # Count total orders from both sources
    total_orders = Sale.query.count() + Order.query.count()
    
    return render_template('admin_dashboard.html',
                         total_products=total_products,
                         total_customers=total_customers,
                         total_revenue=total_revenue,
                         total_orders=total_orders)


# ==================== POS SYSTEM ====================

@admin_bp.route('/pos')
def pos():
    """Admin POS system - display products for quick sale"""
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all products with stock
    products = Product.query.filter(Product.stock > 0).all()
    
    return render_template('admin_pos.html', products=products)


@admin_bp.route('/sales/create', methods=['POST'])
def create_sale():
    """Create POS sale with payment method and discount options"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        discount_type = data.get('discount_type', 'none')
        
        # Validate items
        if not items:
            return jsonify({'error': 'No items in sale'}), 400
        
        # Validate payment method
        if not validate_payment_method(payment_method):
            return jsonify({'error': 'Invalid payment method'}), 400
        
        # Calculate subtotal and validate stock
        subtotal = 0
        for item in items:
            product = Product.query.get(item.get('product_id'))
            
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            quantity = item.get('quantity', 0)
            if not product.is_in_stock(quantity):
                return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
            subtotal += product.price * quantity
        
        # Calculate discount
        discount_amount = calculate_discount(subtotal, discount_type)
        final_total = subtotal - discount_amount
        
        # Update product stock
        for item in items:
            product = Product.query.get(item['product_id'])
            product.reduce_stock(item['quantity'])
        
        # Create sale record
        new_sale = Sale(
            user_id=session.get('user_id'),
            total_amount=final_total,
            payment_method=payment_method,
            discount_type=discount_type if discount_type != 'none' else None,
            discount_amount=discount_amount,
            items=json.dumps(items)
        )
        
        db.session.add(new_sale)
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({
            'success': True,
            'sale_id': new_sale.id,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'final_total': final_total
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create sale'}), 500


@admin_bp.route('/receipt/<int:sale_id>')
def generate_receipt(sale_id):
    """Generate PDF receipt for POS sale"""
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    sale = Sale.query.get_or_404(sale_id)
    buffer = generate_sale_receipt(sale)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'receipt_{sale_id}.pdf',
        mimetype='application/pdf'
    )


# ==================== INVENTORY MANAGEMENT ====================

@admin_bp.route('/inventory')
def inventory():
    """Admin inventory management - view and manage products"""
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Get all products
    products = Product.query.order_by(Product.name).all()
    
    # Prepare products data as JSON for JavaScript
    products_json = json.dumps([product.to_dict() for product in products])
    
    return render_template('admin_inventory.html', 
                         products=products, 
                         products_json=products_json)


@admin_bp.route('/products/add', methods=['POST'])
def add_product():
    """Add new product to inventory"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        
        # Validate product data
        is_valid, error_msg = validate_product_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Create new product
        new_product = Product(
            name=sanitize_string(data['name'], max_length=100),
            description=sanitize_string(data.get('description', '')),
            price=float(data['price']),
            stock=int(data['stock']),
            category=sanitize_string(data.get('category', ''), max_length=50),
            image_url=sanitize_string(data.get('image_url', ''), max_length=200)
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({
            'success': True,
            'product': new_product.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add product'}), 500


@admin_bp.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product details"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        data = request.json
        
        # Validate if updating critical fields
        if 'price' in data or 'stock' in data or 'name' in data:
            is_valid, error_msg = validate_product_data(data)
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # Update fields if provided
        if 'name' in data:
            product.name = sanitize_string(data['name'], max_length=100)
        
        if 'description' in data:
            product.description = sanitize_string(data['description'])
        
        if 'price' in data:
            product.price = float(data['price'])
        
        if 'stock' in data:
            product.stock = int(data['stock'])
        
        if 'category' in data:
            product.category = sanitize_string(data['category'], max_length=50)
        
        if 'image_url' in data:
            product.image_url = sanitize_string(data['image_url'], max_length=200)
        
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update product'}), 500


@admin_bp.route('/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product from inventory"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        
        db.session.delete(product)
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete product'}), 500


# ==================== ORDER MANAGEMENT ====================

@admin_bp.route('/orders')
def get_orders():
    """Get all orders for admin dashboard"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Get all orders from both Order and Sale models
        orders = Order.query.order_by(Order.created_at.desc()).all()
        
        # Convert to list of dictionaries
        orders_list = [order.to_dict() for order in orders]
        
        return jsonify({
            'success': True,
            'orders': orders_list
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch orders'}), 500


@admin_bp.route('/orders/<int:order_id>')
def get_order_details(order_id):
    """Get detailed information about a specific order"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch order details'}), 500


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        data = request.json
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['pending', 'completed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        order.status = new_status
        db.session.commit()
        
        # Export to Excel
        export_to_excel()
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order status'}), 500


@admin_bp.route('/products/list')
def get_products_list():
    """Get all products for admin dashboard"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        products = Product.query.order_by(Product.name).all()
        products_list = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'products': products_list
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch products'}), 500


@admin_bp.route('/products/<int:product_id>/orders')
def get_product_orders(product_id):
    """Get order IDs that contain a specific product"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Get all orders
        orders = Order.query.all()
        order_ids = []
        
        # Check each order's items for the product
        for order in orders:
            try:
                items = json.loads(order.items)
                for item in items:
                    if item.get('product_id') == product_id:
                        order_ids.append(order.id)
                        break  # Only add order ID once
            except:
                continue
        
        return jsonify({
            'success': True,
            'order_ids': sorted(order_ids, reverse=True)  # Most recent first
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch product orders'}), 500


@admin_bp.route('/revenue')
def get_revenue_breakdown():
    """Get revenue breakdown for admin dashboard"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Calculate revenue from orders
        orders = Order.query.all()
        orders_revenue = sum(order.total_amount for order in orders)
        orders_count = len(orders)
        
        # Calculate revenue from POS sales
        sales = Sale.query.all()
        pos_revenue = sum(sale.total_amount for sale in sales)
        pos_count = len(sales)
        
        total_revenue = orders_revenue + pos_revenue
        avg_order_value = total_revenue / (orders_count + pos_count) if (orders_count + pos_count) > 0 else 0
        
        return jsonify({
            'success': True,
            'revenue': {
                'total': total_revenue,
                'from_orders': orders_revenue,
                'from_pos': pos_revenue,
                'orders_count': orders_count,
                'pos_count': pos_count,
                'avg_order_value': avg_order_value
            }
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch revenue'}), 500


# ==================== IMAGE UPLOAD ====================

@admin_bp.route('/products/upload-image', methods=['POST'])
def upload_product_image():
    """Upload product image file"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is an image
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'File must be an image'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'static', 'images', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate secure filename with timestamp
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        # Save file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Return URL path
        image_url = f'/static/images/uploads/{filename}'
        
        return jsonify({
            'success': True,
            'image_url': image_url
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to upload image'}), 500