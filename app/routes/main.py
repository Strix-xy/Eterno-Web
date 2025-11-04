"""
ETERNO E-Commerce Platform - Main Public Routes
Handles public pages accessible to all visitors
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page - show homepage"""
    return render_template('landing.html')