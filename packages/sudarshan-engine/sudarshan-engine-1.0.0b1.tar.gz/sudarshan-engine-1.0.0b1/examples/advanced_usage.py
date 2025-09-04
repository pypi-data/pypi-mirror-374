#!/usr/bin/env python3
"""
Sudarshan Engine - Advanced Usage Examples

This example demonstrates advanced features of the Sudarshan Engine:
- Digital signatures for authentication
- Compression options
- Custom metadata
- Key management
- Batch operations
- Error handling

Run this example:
    python examples/advanced_usage.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudarshan import (
    generate_keypair, spq_create, spq_read, spq_info,
    validate_spq_file, save_keypair_to_file, load_keypair_from_file,
    SPQWorkflowError, SPQFileManager
)


def main():
    """Demonstrate advanced Sudarshan Engine usage"""

    print("🔐 Sudarshan Engine - Advanced Usage Examples")
    print("=" * 55)

    try:
        # Step 1: Generate multiple keypairs
        print("🔑 Step 1: Generating multiple keypairs...")

        # KEM keypair for encryption
        kem_keys = generate_keypair("kem", "kyber1024")
        print("✓ KEM keypair generated (Kyber1024)")

        # Signature keypair for authentication
        sig_keys = generate_keypair("signature", "dilithium5")
        print("✓ Signature keypair generated (Dilithium5)")
        print()

        # Step 2: Save and load keys
        print("💾 Step 2: Key management...")

        # Save keys to files
        save_keypair_to_file(kem_keys, "kem_keys.json")
        save_keypair_to_file(sig_keys, "sig_keys.json")
        print("✓ Keys saved to files")

        # Load keys from files
        loaded_kem_keys = load_keypair_from_file("kem_keys.json")
        loaded_sig_keys = load_keypair_from_file("sig_keys.json")
        print("✓ Keys loaded from files")
        print()

        # Step 3: Create signed .spq files
        print("🔒 Step 3: Creating signed .spq files...")

        # Test data with different sizes and types
        test_cases = [
            {
                "name": "small_text",
                "data": "This is a small text file for testing.",
                "compression": "none",
                "metadata": {"type": "text", "size": "small"}
            },
            {
                "name": "large_text",
                "data": "Large text content\n" * 1000,
                "compression": "zstd",
                "metadata": {"type": "text", "size": "large", "lines": 1000}
            },
            {
                "name": "json_data",
                "data": json.dumps({
                    "users": [{"id": i, "name": f"User{i}"} for i in range(100)],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                "compression": "zstd",
                "metadata": {"type": "json", "records": 100, "format": "user_data"}
            }
        ]

        created_files = []

        for i, test_case in enumerate(test_cases, 1):
            filename = f"advanced_{test_case['name']}.spq"

            # Create comprehensive metadata
            metadata = {
                "author": "Advanced Example",
                "created_by": "advanced_usage.py",
                "version": "1.0",
                "purpose": "Advanced feature demonstration",
                "test_case": test_case['name'],
                "original_size": len(test_case['data']),
                "created_at": datetime.now(timezone.utc).isoformat(),
                **test_case['metadata']
            }

            # Create .spq file with signature
            result = spq_create(
                test_case['data'],
                kem_keys["public_key_bytes"],
                filename,
                sender_secret_key=sig_keys["secret_key_bytes"],
                metadata=metadata,
                compression=test_case['compression'],
                algorithm="kyber1024"
            )

            created_files.append(filename)
            print(f"  ✓ Created {filename} ({result['file_size']} bytes, {test_case['compression']} compression)")

        print()

        # Step 4: Batch file information
        print("📋 Step 4: Batch file information...")
        for filename in created_files:
            info = spq_info(filename)
            if info:
                print(f"  📄 {filename}:")
                print(f"    Algorithm: {info['algorithm']}")
                print(f"    Compression: {info['compression']}")
                print(f"    Size: {info['total_size']} bytes")
                print(f"    Has signature: {'✓' if info['has_signature'] else '✗'}")
        print()

        # Step 5: Batch validation
        print("🔍 Step 5: Batch security validation...")
        for filename in created_files:
            validation = validate_spq_file(filename)
            status = "✓ Secure" if validation['overall_secure'] else "✗ Issues"
            print(f"  🔒 {filename}: {status}")
        print()

        # Step 6: Read and verify signed files
        print("🔓 Step 6: Reading and verifying signed files...")
        for filename in created_files:
            # Read with signature verification
            decrypted = spq_read(
                filename,
                kem_keys["secret_key_bytes"],
                sender_public_key=sig_keys["public_key_bytes"]
            )

            print(f"  ✓ {filename}:")
            print(f"    Decrypted size: {len(decrypted['payload'])} bytes")
            print(f"    Integrity verified: {'✓' if decrypted['integrity_verified'] else '✗'}")
            print(f"    Signature verified: {'✓' if decrypted['signature_verified'] else '✗'}")

            # Verify metadata
            if 'metadata' in decrypted:
                metadata = decrypted['metadata']
                print(f"    Author: {metadata.get('author', 'Unknown')}")
                print(f"    Purpose: {metadata.get('purpose', 'Unknown')}")
        print()

        # Step 7: Demonstrate SPQFileManager
        print("🛠️  Step 7: Using SPQFileManager...")
        manager = SPQFileManager()

        # Create a file using the manager
        test_content = "Content created with SPQFileManager"
        manager_result = manager.encrypt_file(
            "README.md",  # This file should exist
            "managed.spq",
            kem_keys["public_key_bytes"],
            metadata={"managed": True, "tool": "SPQFileManager"}
        )
        print(f"  ✓ File encrypted using manager: {manager_result['filepath']}")

        # Read it back
        manager_decrypt = manager.decrypt_file(
            "managed.spq",
            "managed_decrypted.txt",
            kem_keys["secret_key_bytes"]
        )
        print(f"  ✓ File decrypted using manager: {len(manager_decrypt['payload'])} bytes")
        created_files.extend(["managed.spq", "managed_decrypted.txt"])
        print()

        # Step 8: Error handling demonstration
        print("⚠️  Step 8: Error handling demonstration...")

        # Try to read non-existent file
        try:
            spq_read("nonexistent.spq", kem_keys["secret_key_bytes"])
        except SPQWorkflowError as e:
            print(f"  ✓ Correctly caught error for non-existent file: {str(e)[:50]}...")

        # Try to read with wrong key
        wrong_keys = generate_keypair("kem", "kyber1024")
        try:
            spq_read(created_files[0], wrong_keys["secret_key_bytes"])
        except SPQWorkflowError as e:
            print(f"  ✓ Correctly caught error for wrong key: {str(e)[:50]}...")
        print()

        print("🎉 All advanced usage examples completed successfully!")
        print()
        print("📁 Files created:")
        for filename in created_files:
            if os.path.exists(filename):
                print(f"  - {filename}")
        print()
        print("🔧 Advanced features demonstrated:")
        print("  - Digital signatures for authentication")
        print("  - Multiple compression algorithms")
        print("  - Rich metadata support")
        print("  - Key file management")
        print("  - Batch operations")
        print("  - Error handling")
        print("  - SPQFileManager convenience class")

    except SPQWorkflowError as e:
        print(f"❌ Sudarshan Engine Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        cleanup_files = [
            "kem_keys.json", "sig_keys.json",
            "advanced_small_text.spq", "advanced_large_text.spq", "advanced_json_data.spq",
            "managed.spq", "managed_decrypted.txt"
        ]

        print("\n🧹 Cleaning up example files...")
        for filename in cleanup_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  ✓ Removed {filename}")

        print("✓ Cleanup completed")


if __name__ == "__main__":
    main()