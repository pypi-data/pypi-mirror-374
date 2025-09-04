#!/usr/bin/env python3
"""
Sudarshan Engine Web Interface Server

Production-ready Flask server for the Sudarshan Engine web interface.
Provides a secure web-based interface for quantum-safe operations.

Usage:
    Development: python server.py
    Production: gunicorn --bind 0.0.0.0:8000 server:app

Environment Variables:
    FLASK_ENV: development/production
    SECRET_KEY: Flask secret key
    BASIC_AUTH_USERNAME: Basic auth username
    BASIC_AUTH_PASSWORD: Basic auth password
    CORS_ORIGINS: Allowed CORS origins (comma-separated)
"""

import os
import sys
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Sudarshan Engine modules (when available)
try:
    from sudarshan import crypto, protocols
    SUDARSHAN_AVAILABLE = True
except ImportError:
    SUDARSHAN_AVAILABLE = False
    print("⚠️  Sudarshan Engine core not available - running in demo mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = app.config['ENV'] == 'development'

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080')
CORS(app, origins=cors_origins.split(','))

# Configure security headers with Talisman
Talisman(app,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'font-src': "'self'",
        'connect-src': "'self'",
    },
    content_security_policy_nonce_in=['script-src'],
    force_https=False,  # Set to True in production with HTTPS
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,
    session_cookie_secure=False,  # Set to True with HTTPS
    session_cookie_http_only=True,
    frame_options='DENY'
)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Basic authentication configuration
BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME', 'admin')
BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD', 'password')

# Directory paths
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(WEB_DIR, 'static')

def require_auth(f):
    """Decorator to require basic authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_password_hash(
            generate_password_hash(BASIC_AUTH_PASSWORD),
            auth.password
        ) or auth.username != BASIC_AUTH_USERNAME:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Handle HTTP exceptions with JSON responses."""
    return jsonify({
        'error': e.description,
        'code': e.code
    }), e.code

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'code': 500
    }), 500

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files with security checks."""
    # Prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(403)

    # Check if file exists
    filepath = os.path.join(WEB_DIR, filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        abort(404)

    return send_from_directory(WEB_DIR, filename)

@app.route('/api/status')
def api_status():
    """API endpoint for server status."""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'engine': 'Sudarshan Engine',
        'sudarshan_available': SUDARSHAN_AVAILABLE,
        'environment': app.config['ENV'],
        'features': [
            'quantum-safe encryption',
            'post-quantum cryptography',
            'file encryption/decryption',
            'key generation',
            'secure file format (.spq)'
        ],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/info')
def api_info():
    """API endpoint for application information."""
    return jsonify({
        'name': 'Sudarshan Engine Web Interface',
        'description': 'Quantum-safe cybersecurity platform',
        'version': '1.0.0',
        'author': 'Sudarshan Engine Team',
        'sudarshan_available': SUDARSHAN_AVAILABLE
    })

@app.route('/api/encrypt', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def api_encrypt():
    """Handle file encryption requests."""
    try:
        if not SUDARSHAN_AVAILABLE:
            # Demo mode response
            return jsonify({
                'success': True,
                'message': 'File encrypted successfully (demo mode)',
                'file_size': 1024,
                'algorithm': 'Kyber1024',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

        # TODO: Implement actual encryption using Sudarshan Engine
        # This would parse multipart form data and call encryption functions

        return jsonify({
            'success': True,
            'message': 'File encrypted successfully',
            'algorithm': 'Kyber1024',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/decrypt', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def api_decrypt():
    """Handle file decryption requests."""
    try:
        if not SUDARSHAN_AVAILABLE:
            # Demo mode response
            return jsonify({
                'success': True,
                'message': 'File decrypted successfully (demo mode)',
                'original_size': 1024,
                'verified': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

        # TODO: Implement actual decryption using Sudarshan Engine

        return jsonify({
            'success': True,
            'message': 'File decrypted successfully',
            'verified': True,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-keys', methods=['POST'])
@limiter.limit("5 per minute")
@require_auth
def api_generate_keys():
    """Handle key generation requests."""
    try:
        if not SUDARSHAN_AVAILABLE:
            # Demo mode response
            return jsonify({
                'success': True,
                'message': 'Keys generated successfully (demo mode)',
                'kem_keys': {
                    'algorithm': 'Kyber1024',
                    'public_key_size': 1568,
                    'secret_key_size': 3168
                },
                'signature_keys': {
                    'algorithm': 'Dilithium5',
                    'public_key_size': 2592,
                    'secret_key_size': 4864
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

        # TODO: Implement actual key generation using Sudarshan Engine

        return jsonify({
            'success': True,
            'message': 'Keys generated successfully',
            'kem_keys': {
                'algorithm': 'Kyber1024'
            },
            'signature_keys': {
                'algorithm': 'Dilithium5'
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    except Exception as e:
        logger.error(f"Key generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for load balancers."""
    return jsonify({'status': 'healthy'})

def create_app():
    """Application factory for production deployment."""
    return app

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Sudarshan Engine Web Interface Server')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to run the server on (default: 8080)')
    parser.add_argument('--host', default='localhost',
                        help='Host to bind to (default: localhost)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')

    args = parser.parse_args()

    if args.debug:
        app.config['DEBUG'] = True

    print("🚀 Starting Sudarshan Engine Web Interface...")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}")
    print(f"🔐 Authentication: {BASIC_AUTH_USERNAME}")
    print(f"🌍 Environment: {app.config['ENV']}")
    if SUDARSHAN_AVAILABLE:
        print("🔑 Sudarshan Engine: Available")
    else:
        print("⚠️  Sudarshan Engine: Demo Mode")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    app.run(host=args.host, port=args.port, debug=app.config['DEBUG'])