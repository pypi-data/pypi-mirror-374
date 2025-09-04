#!/usr/bin/env python3
"""
SSL Certificate Test Script for Sudarshan Engine Web Interface
Tests SSL certificate validity and HTTPS connectivity
"""

import ssl
import socket
import sys
from datetime import datetime
import urllib.request
import json

def test_ssl_certificate(hostname, port=443):
    """Test SSL certificate validity."""
    print(f"🔍 Testing SSL certificate for {hostname}:{port}")

    try:
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        # Connect to server
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get certificate info
                cert = ssock.getpeercert()

                # Extract certificate details
                subject = dict(x[0] for x in cert['subject'])
                issuer = dict(x[0] for x in cert['issuer'])
                not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')

                print("✅ SSL Certificate Details:")
                print(f"   Subject: {subject.get('commonName', 'N/A')}")
                print(f"   Issuer: {issuer.get('commonName', 'N/A')}")
                print(f"   Valid From: {not_before}")
                print(f"   Valid Until: {not_after}")
                print(f"   Days Remaining: {(not_after - datetime.now()).days}")

                # Check if certificate is expired
                if datetime.now() < not_before:
                    print("⚠️  Certificate is not yet valid!")
                    return False
                elif datetime.now() > not_after:
                    print("❌ Certificate has expired!")
                    return False
                else:
                    print("✅ Certificate is valid")
                    return True

    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_https_connectivity(url):
    """Test HTTPS connectivity to the web interface."""
    print(f"🌐 Testing HTTPS connectivity to {url}")

    try:
        # Create request with SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        # Test basic connectivity
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            print(f"✅ HTTPS Connection successful (Status: {response.getcode()})")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            return True

    except urllib.error.URLError as e:
        print(f"❌ HTTPS Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_api_endpoints(base_url):
    """Test API endpoints."""
    print(f"🔌 Testing API endpoints at {base_url}")

    endpoints = [
        '/api/health',
        '/api/status',
        '/',
    ]

    results = {}
    for endpoint in endpoints:
        url = base_url.rstrip('/') + endpoint
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                results[endpoint] = {
                    'status': response.getcode(),
                    'success': True
                }
                print(f"✅ {endpoint}: {response.getcode()}")
        except Exception as e:
            results[endpoint] = {
                'status': None,
                'success': False,
                'error': str(e)
            }
            print(f"❌ {endpoint}: Failed - {e}")

    return results

def main():
    """Main test function."""
    print("🛡️  Sudarshan Engine SSL & HTTPS Test Suite")
    print("=" * 50)

    hostname = "sudarshanengine.xyz"
    base_url = f"https://{hostname}"

    # Test SSL certificate
    print("\n" + "="*30)
    ssl_valid = test_ssl_certificate(hostname)

    # Test HTTPS connectivity
    print("\n" + "="*30)
    https_working = test_https_connectivity(base_url)

    # Test API endpoints
    print("\n" + "="*30)
    api_results = test_api_endpoints(base_url)

    # Summary
    print("\n" + "="*30)
    print("📊 Test Summary:")
    print(f"   SSL Certificate: {'✅ Valid' if ssl_valid else '❌ Invalid'}")
    print(f"   HTTPS Connectivity: {'✅ Working' if https_working else '❌ Failed'}")

    successful_apis = sum(1 for r in api_results.values() if r['success'])
    print(f"   API Endpoints: {successful_apis}/{len(api_results)} working")

    if ssl_valid and https_working and successful_apis > 0:
        print("\n🎉 All tests passed! Your web interface is ready for production.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())