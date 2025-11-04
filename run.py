"""
ETERNO E-Commerce Platform - Application Entry Point
Run this file to start the Flask application
"""
import os
from app import create_app

# Get configuration from environment or use default
config_name = os.environ.get('FLASK_CONFIG', 'development')

# Create Flask application instance
app = create_app(config_name)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )