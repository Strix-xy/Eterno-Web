"""
ETERNO E-Commerce Platform - Authentication Utilities
Functions and decorators for user authentication and authorization
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    """
    Decorator to require user login for route access
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin role for route access
    Redirects to login if not authenticated or not admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """
    Decorator to require customer role for route access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'customer':
            flash('Customer access only', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """
    Hash a password for secure storage
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """
    Verify a password against its hash
    
    Args:
        password_hash: Stored password hash
        password: Plain text password to verify
    
    Returns:
        Boolean indicating if password matches
    """
    return check_password_hash(password_hash, password)

def create_user_session(user):
    """
    Create session data for authenticated user
    
    Args:
        user: User model instance
    """
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session.permanent = True

def clear_user_session():
    """Clear all user session data"""
    session.clear()

def get_current_user_id():
    """
    Get the current user's ID from session
    
    Returns:
        User ID or None if not authenticated
    """
    return session.get('user_id')

def get_current_user_role():
    """
    Get the current user's role from session
    
    Returns:
        User role ('admin', 'customer') or None
    """
    return session.get('role')

def is_authenticated():
    """
    Check if user is authenticated
    
    Returns:
        Boolean indicating if user is logged in
    """
    return 'user_id' in session

def is_admin():
    """
    Check if current user is admin
    
    Returns:
        Boolean indicating if user has admin role
    """
    return session.get('role') == 'admin'