"""
ETERNO E-Commerce Platform - Application Factory
Creates and configures the Flask application instance
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """
    Application factory pattern
    Creates and configures the Flask application
    
    Args:
        config_name: Configuration to use (development, production, pythonanywhere, testing)
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask app - handle different environments
    import os
    from pathlib import Path

    # Prefer an external theme when available, but gracefully fall back
    # to this repository's built-in app/templates and app/static folders.
    theme_root_env = os.environ.get('LOOPH_THEME_ROOT')
    external_templates = None
    external_static = None
    use_external_theme = False
    if theme_root_env:
        theme_root = Path(theme_root_env)
        external_templates = theme_root / 'templates'
        external_static = theme_root / 'static'
        use_external_theme = external_templates.exists() and external_static.exists()

    flask_kwargs = {}
    if use_external_theme:
        flask_kwargs.update({
            'template_folder': str(external_templates),
            'static_folder': str(external_static),
            'static_url_path': '/static'
        })

    if config_name in ('vercel', 'pythonanywhere'):
        # For serverless/hosting environments, don't use instance folder in root
        app = Flask(__name__, **flask_kwargs)
    else:
        # For local development, use instance folder
        basedir = os.path.abspath(os.path.dirname(__file__))
        instance_path = os.path.join(os.path.dirname(basedir), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        app = Flask(
            __name__,
            instance_path=instance_path,
            instance_relative_config=True,
            **flask_kwargs
        )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register custom Jinja2 filters
    from app.utils.helpers import format_peso
    app.jinja_env.filters['peso'] = format_peso
    
    @app.context_processor
    def inject_public_config():
        """Expose safe public config values to templates."""
        return {
            'CLERK_PUBLISHABLE_KEY': app.config.get('CLERK_PUBLISHABLE_KEY', ''),
            'CLERK_ENABLED': bool(app.config.get('CLERK_PUBLISHABLE_KEY'))
        }
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.customer import customer_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp)
    
    # Initialize database and create default data
    with app.app_context():
        from app.utils.db_init import init_database
        init_database()
    
    return app