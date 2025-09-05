#!/usr/bin/env python3
"""
Unit Tests for Sudarshan Engine Cryptographic Operations

Tests quantum-safe cryptographic primitives and operations.
"""

import pytest
import secrets
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import components to test
from sudarshan.crypto import SudarshanCrypto, get_crypto_instance

# Check OQS availability
try:
    from bindings.oqs_bindings import OQSBindings
    oqs_available = True
except ImportError:
    oqs_available = False

# Simple test utilities
def get_test_data(size: int) -> bytes:
    """Generate test data of specified size."""
    return secrets.token_bytes(size)


class TestSudarshanCrypto:
    """Test Sudarshan crypto operations."""

    def setup_method(self):
        self.crypto = SudarshanCrypto()

    @pytest.mark.skipif(not oqs_available, reason="OQS not available")
    def test_kem_keypair_generation(self):
        """Test KEM keypair generation."""
        public_key, secret_key = self.crypto.generate_kem_keypair()

        assert public_key is not None
        assert secret_key is not None
        assert len(public_key) > 0
        assert len(secret_key) > 0
        assert public_key != secret_key  # Keys should be different

    @pytest.mark.skipif(not oqs_available, reason="OQS not available")
    def test_signature_keypair_generation(self):
        """Test signature keypair generation."""
        public_key, secret_key = self.crypto.generate_signature_keypair()

        assert public_key is not None
        assert secret_key is not None
        assert len(public_key) > 0
        assert len(secret_key) > 0
        assert public_key != secret_key  # Keys should be different

    @pytest.mark.skipif(not oqs_available, reason="OQS not available")
    def test_kem_encapsulation_decapsulation(self):
        """Test KEM encapsulation and decapsulation."""
        # Generate keypair
        public_key, secret_key = self.crypto.generate_kem_keypair()

        # Encapsulate shared secret
        ciphertext, shared_secret_enc = self.crypto.encapsulate_key(public_key)

        # Decapsulate shared secret
        shared_secret_dec = self.crypto.decapsulate_key(ciphertext, secret_key)

        assert shared_secret_enc is not None
        assert shared_secret_dec is not None
        assert shared_secret_enc == shared_secret_dec  # Should be identical
        assert len(shared_secret_enc) == 32  # Kyber shared secret is 32 bytes

    @pytest.mark.skipif(not oqs_available, reason="OQS not available")
    def test_signature_generation_verification(self):
        """Test signature generation and verification."""
        # Generate signature keypair
        public_key, secret_key = self.crypto.generate_signature_keypair()

        # Sign message
        message = b"Hello, quantum world!"
        signature = self.crypto.sign_data(message, secret_key)

        # Verify signature
        is_valid = self.crypto.verify_signature(message, signature, public_key)

        assert signature is not None
        assert len(signature) > 0
        assert is_valid is True

    @pytest.mark.skipif(not oqs_available, reason="OQS not available")
    def test_signature_verification_failure(self):
        """Test signature verification failure with wrong message."""
        # Generate signature keypair
        public_key, secret_key = self.crypto.generate_signature_keypair()

        # Sign message
        message = b"Hello, quantum world!"
        signature = self.crypto.sign_data(message, secret_key)

        # Try to verify with different message
        wrong_message = b"Goodbye, quantum world!"
        is_valid = self.crypto.verify_signature(wrong_message, signature, public_key)

        assert is_valid is False

    def test_symmetric_encryption_decryption(self):
        """Test symmetric encryption/decryption."""
        test_data = b"Hello, quantum world!"
        key = secrets.token_bytes(32)

        # Encrypt
        encrypted = self.crypto.encrypt_data(test_data, key)

        # Decrypt
        decrypted = self.crypto.decrypt_data(
            encrypted['ciphertext'],
            key,
            encrypted['nonce'],
            encrypted['tag']
        )

        assert encrypted is not None
        assert decrypted == test_data

    def test_hash_integrity(self):
        """Test hash integrity."""
        data = get_test_data(2048)
        hash_value = self.crypto.hash_data(data, "sha3_512")

        assert hash_value is not None
        assert len(hash_value) == 64  # SHA3-512 produces 64 bytes

        # Same data should produce same hash
        hash_value2 = self.crypto.hash_data(data, "sha3_512")
        assert hash_value == hash_value2

        # Different data should produce different hash
        different_data = data + b"x"
        hash_value3 = self.crypto.hash_data(different_data, "sha3_512")
        assert hash_value != hash_value3

    def test_key_derivation(self):
        """Test key derivation from shared secret."""
        shared_secret = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)

        derived_key = self.crypto.derive_key(shared_secret, salt, b"test", 32)

        assert derived_key is not None
        assert len(derived_key) == 32

        # Same inputs should produce same key
        derived_key2 = self.crypto.derive_key(shared_secret, salt, b"test", 32)
        assert derived_key == derived_key2

        # Different salt should produce different key
        different_salt = secrets.token_bytes(16)
        derived_key3 = self.crypto.derive_key(shared_secret, different_salt, b"test", 32)
        assert derived_key != derived_key3

    def test_invalid_algorithm_handling(self):
        """Test handling of invalid algorithms."""
        # Test with invalid algorithm - should raise KeyDerivationError or OQSError
        with pytest.raises((ValueError, Exception)):  # Accept any exception for invalid algorithm
            self.crypto.generate_kem_keypair("InvalidAlgorithm")  # Wrong algorithm type

    def test_encryption_bounds_checking(self):
        """Test encryption bounds checking."""
        # Test empty data
        with pytest.raises(Exception):  # Should raise EncryptionError
            self.crypto.encrypt_data(b"", secrets.token_bytes(32))

        # Test wrong key size (16 bytes instead of 32)
        with pytest.raises(Exception):  # Should raise EncryptionError
            self.crypto.encrypt_data(b"test", secrets.token_bytes(16))  # Wrong key size

        # Test oversized associated data (should fail)
        test_data = b"test data"
        key = secrets.token_bytes(32)
        oversized_aad = secrets.token_bytes(70000)  # > 64KB limit
        with pytest.raises(Exception):  # Should raise EncryptionError
            self.crypto.encrypt_data(test_data, key, oversized_aad)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])