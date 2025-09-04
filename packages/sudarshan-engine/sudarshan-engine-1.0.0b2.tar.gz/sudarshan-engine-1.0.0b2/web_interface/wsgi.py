#!/usr/bin/env python3
"""
WSGI entry point for Sudarshan Engine Web Interface

This file serves as the WSGI application entry point for production deployment
with servers like Gunicorn, uWSGI, or other WSGI-compatible servers.

Usage:
    gunicorn --bind 0.0.0.0:8000 wsgi:app
    uwsgi --http :8000 --wsgi-file wsgi.py --callable app
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the Flask application
from server import create_app

# Create the WSGI application
app = create_app()

if __name__ == '__main__':
    # For development testing
    app.run(
        host=os.getenv('HOST', 'localhost'),
        port=int(os.getenv('PORT', 8080)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )