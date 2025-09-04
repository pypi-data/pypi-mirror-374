#!/usr/bin/env python3
"""
Gunicorn configuration for Sudarshan Engine Web Interface

This configuration file is used when deploying with Gunicorn in production.

Usage:
    gunicorn --config gunicorn.conf.py wsgi:app
"""

import os
import multiprocessing

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, with a jitter
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
accesslog = os.getenv('ACCESS_LOG', '-')
errorlog = os.getenv('ERROR_LOG', '-')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'sudarshan_web'

# Server mechanics
preload_app = True
pidfile = '/tmp/gunicorn_sudarshan.pid'
user = os.getenv('GUNICORN_USER')
group = os.getenv('GUNICORN_GROUP')
tmp_upload_dir = None

# SSL (if configured)
keyfile = os.getenv('SSL_KEY_PATH')
certfile = os.getenv('SSL_CERT_PATH')

# Application
wsgi_module = 'wsgi:app'
pythonpath = os.path.dirname(os.path.abspath(__file__))

# Development overrides
if os.getenv('FLASK_ENV') == 'development':
    workers = 1
    loglevel = 'debug'
    reload = True