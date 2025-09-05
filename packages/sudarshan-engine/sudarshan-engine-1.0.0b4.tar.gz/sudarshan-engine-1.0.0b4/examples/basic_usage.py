#!/usr/bin/env python3
"""
Sudarshan Engine - Basic Usage Examples

This script demonstrates the fundamental operations of the Sudarshan Engine
for quantum-safe file encryption and decryption.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sudarshan import spq_create, spq_read


def example_basic_encryption():
    """Example 1: Basic file encryption with default settings."""
    print("🔐 Example 1: Basic File Encryption")
    print("-" * 40)

    # Sample data to encrypt
    secret_data = b"This is a secret message that needs quantum-safe protection!"

    # Basic metadata
    metadata = {
        "title": "Secret Document",
        "author": "Sudarshan User",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "classification": "confidential"
    }

    print(f"📝 Original data size: {len(secret_data)} bytes")
    print(f"📋 Metadata: {json.dumps(metadata, indent=2)}")

    # Create .spq file
    result = spq_create(
        data=secret_data,
        metadata=metadata,
        algorithm="kyber1024",  # Default quantum-safe algorithm
        compression="zstd"     # Default compression
    )

    print("✅ Encryption successful!")
    print(f"📁 Encrypted file size: {len(result['data'])} bytes")
    print(f"🔢 Algorithm used: {result.get('algorithm', 'kyber1024')}")
    print(f"🗜️  Compression: {result.get('compression', 'zstd')}")
    print()

    return result


def example_basic_decryption(encrypted_data):
    """Example 2: Basic file decryption."""
    print("🔓 Example 2: Basic File Decryption")
    print("-" * 40)

    print(f"📁 Encrypted data size: {len(encrypted_data)} bytes")

    # Decrypt .spq file
    result = spq_read(data=encrypted_data)

    print("✅ Decryption successful!")
    print(f"📝 Decrypted data size: {len(result['data'])} bytes")
    print(f"📋 Recovered metadata: {json.dumps(result['metadata'], indent=2)}")
    print(f"💬 Original message: {result['data'].decode()}")
    print()

    return result


def example_custom_metadata():
    """Example 3: Encryption with custom metadata and different algorithms."""
    print("🎨 Example 3: Custom Metadata & Algorithms")
    print("-" * 40)

    # More complex data
    document_data = {
        "title": "Research Paper on Quantum Cryptography",
        "abstract": "This paper explores the latest developments in post-quantum cryptography...",
        "authors": ["Dr. Alice Quantum", "Prof. Bob Crypto"],
        "publication_date": "2025-09-02",
        "keywords": ["quantum", "cryptography", "PQC", "security"],
        "confidential": True
    }

    # Convert to JSON bytes
    data_bytes = json.dumps(document_data, indent=2).encode()

    # Rich metadata
    metadata = {
        "document_type": "research_paper",
        "version": "1.0",
        "language": "en",
        "created_by": "sudarshan_engine",
        "created_at": datetime.now().isoformat() + "Z",
        "expires_at": "2026-09-02T00:00:00Z",
        "permissions": ["read", "write"],
        "tags": ["research", "quantum", "confidential"],
        "checksum": "sha256:" + "placeholder_hash"
    }

    print(f"📄 Document data size: {len(data_bytes)} bytes")
    print(f"🏷️  Metadata fields: {len(metadata)}")

    # Encrypt with different algorithm
    result = spq_create(
        data=data_bytes,
        metadata=metadata,
        algorithm="kyber768",  # Different algorithm
        compression="lz4"      # Different compression
    )

    print("✅ Custom encryption successful!")
    print(f"🔢 Algorithm: {result.get('algorithm', 'kyber768')}")
    print(f"🗜️  Compression: {result.get('compression', 'lz4')}")
    print()

    return result


def example_file_operations():
    """Example 4: File-based operations (save/load from disk)."""
    print("💾 Example 4: File-Based Operations")
    print("-" * 40)

    # Create test data
    test_data = b"File-based encryption/decryption test data"
    metadata = {
        "operation": "file_test",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Encrypt and save to file
    result = spq_create(
        data=test_data,
        metadata=metadata,
        algorithm="kyber1024",
        compression="none"
    )

    # Save encrypted data to file
    output_file = "test_document.spq"
    with open(output_file, 'wb') as f:
        f.write(result['data'])

    print(f"💾 Encrypted file saved: {output_file}")
    print(f"📁 File size: {len(result['data'])} bytes")

    # Read back from file
    with open(output_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt
    decrypted = spq_read(data=encrypted_data)

    print("✅ File round-trip successful!")
    print(f"📝 Original: {test_data.decode()}")
    print(f"📝 Decrypted: {decrypted['data'].decode()}")

    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"🗑️  Cleaned up: {output_file}")

    print()
    return decrypted


def example_error_handling():
    """Example 5: Error handling and edge cases."""
    print("⚠️  Example 5: Error Handling")
    print("-" * 40)

    # Test with invalid data
    try:
        invalid_result = spq_read(data=b"not_a_valid_spq_file")
        print("❌ Should have failed!")
    except Exception as e:
        print(f"✅ Correctly caught invalid file error: {type(e).__name__}")

    # Test with empty data
    try:
        empty_result = spq_create(data=b"", metadata={})
        print("✅ Empty data encryption successful")
        print(f"📁 Encrypted size: {len(empty_result['data'])} bytes")
    except Exception as e:
        print(f"❌ Empty data failed: {e}")

    # Test with large metadata
    large_metadata = {"data": "x" * 10000}  # 10KB metadata
    try:
        large_result = spq_create(
            data=b"test",
            metadata=large_metadata,
            algorithm="kyber512"  # Smaller algorithm
        )
        print("✅ Large metadata encryption successful")
        print(f"📁 Total size: {len(large_result['data'])} bytes")
    except Exception as e:
        print(f"❌ Large metadata failed: {e}")

    print()


def main():
    """Run all basic usage examples."""
    print("🚀 Sudarshan Engine - Basic Usage Examples")
    print("=" * 50)
    print()

    try:
        # Example 1: Basic encryption
        encrypted_result = example_basic_encryption()

        # Example 2: Basic decryption
        decrypted_result = example_basic_decryption(encrypted_result['data'])

        # Example 3: Custom metadata
        custom_result = example_custom_metadata()

        # Example 4: File operations
        file_result = example_file_operations()

        # Example 5: Error handling
        example_error_handling()

        print("🎉 All examples completed successfully!")
        print()
        print("💡 Next steps:")
        print("  • Try the advanced examples: python advanced_usage.py")
        print("  • Explore wallet integration: python wallet_example.py")
        print("  • Run the test suite: python -m pytest tests/")
        print("  • Start the web interface: cd web_interface && python server.py")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure Sudarshan Engine is properly installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()