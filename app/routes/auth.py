"""
ETERNO E-Commerce Platform - Authentication Routes
Handles user login, registration, and logout with enhanced validation
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.utils.helpers import is_valid_email, sanitize_string
from app.utils.export import export_to_excel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login - validates credentials and creates session
    Redirects to appropriate dashboard based on role
    """
    # Redirect if already logged in
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.shop'))
    
    if request.method == 'POST':
        username = sanitize_string(request.form.get('username'), max_length=80)
        password = request.form.get('password', '')
        
        # Validate input
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Verify credentials
        if user and check_password_hash(user.password, password):
            # Create session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('customer.shop'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration - creates new customer account with comprehensive validation
    """
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('customer.shop'))
    
    if request.method == 'POST':
        username = sanitize_string(request.form.get('username'), max_length=80)
        email = sanitize_string(request.form.get('email'), max_length=120)
        password = request.form.get('password', '')
        
        # Validate all fields are provided
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        # Validate username length
        if len(username) < 3:
            return render_template('register.html', error='Username must be at least 3 characters long')
        
        # Validate password strength
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long')
        
        # Validate email format
        if not is_valid_email(email):
            return render_template('register.html', error='Invalid email format')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        try:
            # Create new customer account
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email.lower(),  # Store email in lowercase
                password=hashed_password,
                role='customer'
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Export to Excel
            export_to_excel()
            
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='An error occurred during registration. Please try again.')
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Clear user session and redirect to landing page"""
    session.clear()
    return redirect(url_for('main.index'))