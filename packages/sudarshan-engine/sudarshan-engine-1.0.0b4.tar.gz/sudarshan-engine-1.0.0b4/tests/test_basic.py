#!/usr/bin/env python3
"""
Basic Unit Tests for Sudarshan Engine

Tests core functionality:
- Keypair generation
- .spq file creation and reading
- Basic validation
- Error handling
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudarshan import (
    generate_keypair, spq_create, spq_read, spq_info,
    validate_spq_file, get_engine_info, check_free_tier_limits,
    SPQWorkflowError
)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic Sudarshan Engine functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_data = "Hello, Quantum World! 🌍\n" * 5
        self.test_metadata = {
            "author": "Test Suite",
            "purpose": "Unit Testing",
            "version": "1.0"
        }

        # Generate test keypair
        self.keypair = generate_keypair("kem", "kyber1024")

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove test files
        for filename in os.listdir(self.test_dir):
            filepath = os.path.join(self.test_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        os.rmdir(self.test_dir)

    def test_engine_info(self):
        """Test engine information retrieval"""
        info = get_engine_info()

        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("features", info)
        self.assertEqual(info["name"], "Sudarshan Engine")
        self.assertTrue(info["features"]["quantum_safe"])

    def test_keypair_generation(self):
        """Test PQC keypair generation"""
        # Test KEM keypair
        kem_keys = generate_keypair("kem", "kyber1024")
        self.assertIn("public_key", kem_keys)
        self.assertIn("secret_key", kem_keys)
        self.assertIn("algorithm", kem_keys)
        self.assertEqual(kem_keys["algorithm"], "kyber1024")
        self.assertEqual(len(kem_keys["public_key_bytes"]), 1568)  # Kyber1024 public key size
        self.assertEqual(len(kem_keys["secret_key_bytes"]), 3168)  # Kyber1024 secret key size

        # Test signature keypair
        sig_keys = generate_keypair("signature", "dilithium5")
        self.assertIn("public_key", sig_keys)
        self.assertIn("secret_key", sig_keys)
        self.assertEqual(sig_keys["algorithm"], "dilithium5")

    def test_free_tier_limits(self):
        """Test free tier limit checking"""
        # Test within limits
        result = check_free_tier_limits(1000, 10)
        self.assertTrue(result["within_limits"])
        self.assertEqual(len(result["warnings"]), 0)

        # Test file size limit
        result = check_free_tier_limits(200 * 1024 * 1024, 1)  # 200MB
        self.assertFalse(result["within_limits"])
        self.assertTrue(len(result["warnings"]) > 0)
        self.assertTrue(result["upgrade_required"])

        # Test operation limit
        result = check_free_tier_limits(1000, 2000)
        self.assertFalse(result["within_limits"])
        self.assertTrue(len(result["warnings"]) > 0)

    def test_spq_create_read_basic(self):
        """Test basic .spq file creation and reading"""
        test_file = os.path.join(self.test_dir, "test_basic.spq")

        # Create .spq file
        result = spq_create(
            self.test_data,
            self.keypair["public_key_bytes"],
            test_file,
            metadata=self.test_metadata
        )

        # Verify creation result
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["filepath"], test_file)
        self.assertTrue(os.path.exists(test_file))

        # Read .spq file
        read_result = spq_read(test_file, self.keypair["secret_key_bytes"])

        # Verify read result
        self.assertIn("payload", read_result)
        self.assertEqual(read_result["payload"].decode('utf-8'), self.test_data)
        self.assertTrue(read_result["integrity_verified"])

    def test_spq_info(self):
        """Test .spq file information retrieval"""
        test_file = os.path.join(self.test_dir, "test_info.spq")

        # Create .spq file
        spq_create(
            self.test_data,
            self.keypair["public_key_bytes"],
            test_file,
            metadata=self.test_metadata
        )

        # Get file info
        info = spq_info(test_file)

        self.assertIsNotNone(info)
        self.assertIn("algorithm", info)
        self.assertIn("compression", info)
        self.assertIn("total_size", info)
        self.assertEqual(info["algorithm"], "kyber1024")
        self.assertEqual(info["compression"], "none")

    def test_spq_validation(self):
        """Test .spq file security validation"""
        test_file = os.path.join(self.test_dir, "test_validation.spq")

        # Create .spq file
        spq_create(
            self.test_data,
            self.keypair["public_key_bytes"],
            test_file,
            metadata=self.test_metadata
        )

        # Validate file
        validation = validate_spq_file(test_file)

        self.assertTrue(validation["file_exists"])
        self.assertTrue(validation["format_valid"])
        self.assertTrue(validation["metadata_valid"])
        self.assertTrue(validation["overall_secure"])

    def test_spq_with_compression(self):
        """Test .spq file with compression"""
        test_file = os.path.join(self.test_dir, "test_compressed.spq")

        # Create larger test data for compression
        large_data = "This is test data for compression testing. " * 1000

        # Create .spq file with compression
        result = spq_create(
            large_data,
            self.keypair["public_key_bytes"],
            test_file,
            metadata=self.test_metadata,
            compression="zstd"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["compression"], "zstd")

        # Read and verify
        read_result = spq_read(test_file, self.keypair["secret_key_bytes"])
        self.assertEqual(read_result["payload"].decode('utf-8'), large_data)

    def test_spq_with_signature(self):
        """Test .spq file with digital signature"""
        test_file = os.path.join(self.test_dir, "test_signed.spq")

        # Generate signature keypair
        sig_keys = generate_keypair("signature", "dilithium5")

        # Create .spq file with signature
        result = spq_create(
            self.test_data,
            self.keypair["public_key_bytes"],
            test_file,
            sender_secret_key=sig_keys["secret_key_bytes"],
            metadata=self.test_metadata
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["has_signature"])

        # Read with signature verification
        read_result = spq_read(
            test_file,
            self.keypair["secret_key_bytes"],
            sender_public_key=sig_keys["public_key_bytes"]
        )

        self.assertTrue(read_result["integrity_verified"])
        self.assertTrue(read_result["signature_verified"])

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test reading non-existent file
        with self.assertRaises(SPQWorkflowError):
            spq_read("nonexistent.spq", self.keypair["secret_key_bytes"])

        # Test reading with wrong key
        test_file = os.path.join(self.test_dir, "test_error.spq")
        spq_create(self.test_data, self.keypair["public_key_bytes"], test_file)

        wrong_key = generate_keypair("kem", "kyber1024")
        with self.assertRaises(SPQWorkflowError):
            spq_read(test_file, wrong_key["secret_key_bytes"])

    def test_metadata_handling(self):
        """Test metadata handling in .spq files"""
        test_file = os.path.join(self.test_dir, "test_metadata.spq")

        # Create .spq with rich metadata
        rich_metadata = {
            "author": "Test Suite",
            "created_at": "2025-09-02T08:44:00Z",
            "tags": ["test", "metadata", "quantum-safe"],
            "version": "1.0",
            "permissions": ["read", "write"],
            "expires_at": "2026-09-02T08:44:00Z"
        }

        spq_create(
            self.test_data,
            self.keypair["public_key_bytes"],
            test_file,
            metadata=rich_metadata
        )

        # Read and verify metadata
        read_result = spq_read(test_file, self.keypair["secret_key_bytes"])

        self.assertIn("metadata", read_result)
        metadata = read_result["metadata"]
        self.assertEqual(metadata["author"], "Test Suite")
        self.assertEqual(metadata["version"], "1.0")
        self.assertIn("test", metadata["tags"])


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)