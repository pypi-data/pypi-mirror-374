#!/usr/bin/env python3
"""
Test Script for Sudarshan Engine Web Interface

This script tests the basic functionality of the web interface server.

Usage:
    python test_server.py

Requirements:
    - Flask and related packages must be installed
    - Run from the web_interface directory
"""

import os
import sys
import requests
import time
import subprocess
import signal
import threading
from contextlib import contextmanager

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

SERVER_PROCESS = None

@contextmanager
def run_test_server():
    """Context manager to run the test server."""
    global SERVER_PROCESS

    # Start server in background
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['SECRET_KEY'] = 'test-secret-key'

    SERVER_PROCESS = subprocess.Popen(
        [sys.executable, 'server.py', '--host', 'localhost', '--port', '8081'],
        cwd=os.path.dirname(__file__),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(3)

    try:
        yield
    finally:
        # Clean up
        if SERVER_PROCESS:
            SERVER_PROCESS.terminate()
            SERVER_PROCESS.wait(timeout=5)

def test_server_startup():
    """Test if the server starts successfully."""
    print("🧪 Testing server startup...")

    with run_test_server():
        try:
            response = requests.get('http://localhost:8081/api/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    print("✅ Server startup test passed")
                    return True
                else:
                    print(f"❌ Server health check failed: {data}")
            else:
                print(f"❌ Server returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Server connection failed: {e}")

    print("❌ Server startup test failed")
    return False

def test_api_endpoints():
    """Test API endpoints."""
    print("🧪 Testing API endpoints...")

    with run_test_server():
        base_url = 'http://localhost:8081'
        endpoints = [
            ('/api/status', 'GET'),
            ('/api/info', 'GET'),
            ('/api/health', 'GET'),
        ]

        passed = 0
        total = len(endpoints)

        for endpoint, method in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                else:
                    continue

                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                    passed += 1
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint} - Error: {e}")

        print(f"📊 API endpoints test: {passed}/{total} passed")
        return passed == total

def test_static_files():
    """Test static file serving."""
    print("🧪 Testing static file serving...")

    with run_test_server():
        try:
            response = requests.get('http://localhost:8081/', timeout=5)
            if response.status_code == 200:
                if 'text/html' in response.headers.get('content-type', ''):
                    print("✅ Static file serving test passed")
                    return True
                else:
                    print(f"❌ Wrong content type: {response.headers.get('content-type')}")
            else:
                print(f"❌ Static file request failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Static file request error: {e}")

    print("❌ Static file serving test failed")
    return False

def test_security_headers():
    """Test security headers."""
    print("🧪 Testing security headers...")

    with run_test_server():
        try:
            response = requests.get('http://localhost:8081/', timeout=5)
            headers = response.headers

            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'Strict-Transport-Security'
            ]

            found_headers = [h for h in security_headers if h in headers]
            print(f"✅ Found security headers: {found_headers}")

            if len(found_headers) >= 2:  # At least some security headers
                print("✅ Security headers test passed")
                return True
            else:
                print("⚠️  Few security headers found")

        except requests.exceptions.RequestException as e:
            print(f"❌ Security headers test error: {e}")

    print("❌ Security headers test failed")
    return False

def main():
    """Run all tests."""
    print("🚀 Starting Sudarshan Engine Web Interface Tests")
    print("=" * 50)

    # Check if required packages are available
    try:
        import flask
        import flask_cors
        import flask_talisman
        import flask_limiter
        print("✅ Required packages are available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Install with: pip install flask flask-cors flask-talisman flask-limiter")
        return False

    tests = [
        test_server_startup,
        test_api_endpoints,
        test_static_files,
        test_security_headers,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)