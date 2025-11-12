"""
ETERNO E-Commerce Platform - Database Models
All SQLAlchemy models with optimized relationships and indexes
"""
from datetime import datetime
import json
from app import db
from app.utils.helpers import format_datetime_sg, isoformat_datetime_sg

class User(db.Model):
    """User model for customer and admin accounts"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'admin' or 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships with cascade delete
    carts = db.relationship('Cart', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': isoformat_datetime_sg(self.created_at),
            'created_at_display': format_datetime_sg(self.created_at)
        }


class Product(db.Model):
    """Product model for inventory management"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)  # Price in Philippine Peso
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), index=True)  # e.g., Shirts, Pants, Accessories
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def is_in_stock(self, quantity=1):
        """Check if product has sufficient stock"""
        return self.stock >= quantity
    
    def reduce_stock(self, quantity):
        """Reduce product stock by quantity"""
        if self.is_in_stock(quantity):
            self.stock -= quantity
            return True
        return False
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'stock': self.stock,
            'category': self.category,
            'image_url': self.image_url,
            'created_at': isoformat_datetime_sg(self.created_at),
            'created_at_display': format_datetime_sg(self.created_at) if self.created_at else None
        }


class Sale(db.Model):
    """Sale model for admin POS transactions"""
    __tablename__ = 'sale'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='cash')  # cash, gcash, bank_transfer
    discount_type = db.Column(db.String(50))  # pwd, senior, voucher, none
    discount_amount = db.Column(db.Float, default=0)
    items = db.Column(db.Text, nullable=False)  # JSON string of purchased items
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Sale {self.id}>'
    
    def to_dict(self):
        """Convert sale to dictionary"""
        try:
            items_data = json.loads(self.items or '[]')
        except (TypeError, json.JSONDecodeError):
            items_data = []
        
        subtotal = sum(
            float(item.get('price', 0)) * int(item.get('quantity', 0))
            for item in items_data
        )
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method,
            'discount_type': self.discount_type,
            'discount_amount': self.discount_amount,
            'items': self.items,
            'items_data': items_data,
            'subtotal': subtotal,
            'created_at': isoformat_datetime_sg(self.created_at),
            'created_at_display': format_datetime_sg(self.created_at)
        }


class Cart(db.Model):
    """Shopping cart for customer purchases"""
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate cart items
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
    )
    
    def __repr__(self):
        return f'<Cart user:{self.user_id} product:{self.product_id}>'
    
    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        if self.product:
            return self.product.price * self.quantity
        return 0
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'subtotal': self.get_subtotal()
        }


class Order(db.Model):
    """Order model for customer purchases with shipping details"""
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_address = db.Column(db.Text)
    subtotal = db.Column(db.Float, nullable=False)
    shipping_fee = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cod, gcash, bank_transfer
    items = db.Column(db.Text, nullable=False)  # JSON string of ordered items
    status = db.Column(db.String(50), default='pending', index=True)  # pending, processing, shipped, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def to_dict(self):
        """Convert order to dictionary"""
        try:
            items_data = json.loads(self.items or '[]')
        except (TypeError, json.JSONDecodeError):
            items_data = []
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_address': self.customer_address,
            'subtotal': self.subtotal,
            'shipping_fee': self.shipping_fee,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method,
            'status': self.status,
            'items': self.items,
            'items_data': items_data,
            'created_at': isoformat_datetime_sg(self.created_at),
            'created_at_display': format_datetime_sg(self.created_at)
        }


class ReportCheckpoint(db.Model):
    """Track report reset timestamps per period"""
    __tablename__ = 'report_checkpoint'
    
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(20), unique=True, nullable=False)
    last_reset_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReportCheckpoint {self.period}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'period': self.period,
            'last_reset_at': isoformat_datetime_sg(self.last_reset_at),
            'last_reset_at_display': format_datetime_sg(self.last_reset_at)
        }