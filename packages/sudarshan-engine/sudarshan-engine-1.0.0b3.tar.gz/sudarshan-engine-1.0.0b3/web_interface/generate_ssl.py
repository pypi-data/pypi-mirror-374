#!/usr/bin/env python3
"""
SSL Certificate Generation Script for Sudarshan Engine Web Interface

This script generates self-signed SSL certificates for development and testing.
For production, use certificates from a trusted Certificate Authority.

Usage:
    python generate_ssl.py

This will create:
- ssl/cert.pem (SSL certificate)
- ssl/key.pem (SSL private key)
"""

import os
import sys
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

def generate_ssl_certificates():
    """Generate self-signed SSL certificates."""

    # Create SSL directory
    ssl_dir = os.path.join(os.path.dirname(__file__), 'ssl')
    os.makedirs(ssl_dir, exist_ok=True)

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sudarshan Engine"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write certificate and key files
    cert_path = os.path.join(ssl_dir, 'cert.pem')
    key_path = os.path.join(ssl_dir, 'key.pem')

    with open(cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("✅ SSL certificates generated successfully!")
    print(f"📄 Certificate: {cert_path}")
    print(f🔑 Private Key: {key_path}")
    print("\n⚠️  WARNING: These are self-signed certificates for development only!")
    print("   For production, obtain certificates from a trusted CA.")

if __name__ == '__main__':
    try:
        generate_ssl_certificates()
    except ImportError:
        print("❌ Error: cryptography package is required.")
        print("   Install with: pip install cryptography")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating certificates: {e}")
        sys.exit(1)