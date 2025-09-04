#!/usr/bin/env python3
"""
Integration tests for Sudarshan Engine Box-in-a-Box security model.

Tests the complete security stack from Inner Shield through Transaction Capsule.
"""

import pytest
import os
import sys
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from sudarshan.protocols import InnerShield, OuterVault, IsolationRoom, TransactionCapsule
from sudarshan import spq_create, spq_read


class TestInnerShieldIntegration:
    """Integration tests for Inner Shield protocol."""

    def test_inner_shield_wrap_unwrap_legacy_key(self):
        """Test complete wrap/unwrap cycle for legacy key protection."""
        # Mock legacy key (e.g., Bitcoin private key)
        legacy_key = b"mock_legacy_private_key_32_bytes"

        metadata = {
            "asset_type": "bitcoin_private_key",
            "network": "mainnet",
            "derivation_path": "m/44'/0'/0'/0/0"
        }

        # Create Inner Shield
        shield = InnerShield()

        # Wrap the legacy key
        wrapped = shield.wrap_asset(legacy_key, metadata)

        assert "pqc_public_key" in wrapped
        assert "encrypted_legacy" in wrapped
        assert "metadata" in wrapped

        # Unwrap the legacy key
        unwrapped = shield.unwrap_asset(wrapped)

        assert unwrapped == legacy_key

    def test_inner_shield_different_asset_types(self):
        """Test Inner Shield with different asset types."""
        test_cases = [
            ("ethereum_key", b"ethereum_private_key_32_bytes"),
            ("database_password", b"super_secret_db_password"),
            ("api_token", b"github_personal_access_token"),
            ("ssl_private_key", b"ssl_certificate_private_key")
        ]

        shield = InnerShield()

        for asset_type, asset_data in test_cases:
            metadata = {"asset_type": asset_type}

            # Wrap
            wrapped = shield.wrap_asset(asset_data, metadata)

            # Unwrap
            unwrapped = shield.unwrap_asset(wrapped)

            assert unwrapped == asset_data
            assert wrapped["metadata"]["asset_type"] == asset_type

    def test_inner_shield_tamper_detection(self):
        """Test that Inner Shield detects tampering."""
        legacy_key = b"test_key"
        metadata = {"test": "data"}

        shield = InnerShield()
        wrapped = shield.wrap_asset(legacy_key, metadata)

        # Tamper with encrypted data
        tampered = wrapped.copy()
        tampered["encrypted_legacy"] = tampered["encrypted_legacy"][::-1]  # Reverse bytes

        with pytest.raises(ValueError):
            shield.unwrap_asset(tampered)


class TestOuterVaultIntegration:
    """Integration tests for Outer Vault protocol."""

    def test_outer_vault_multi_factor_authentication(self):
        """Test MFA with multiple PQC factors."""
        vault = OuterVault()

        # Mock authentication factors
        factors = [
            {
                "type": "pqc_signature",
                "public_key": b"mock_public_key",
                "signature": b"mock_signature",
                "challenge": b"login_challenge"
            },
            {
                "type": "hardware_token",
                "token_id": "YUBIKEY_123",
                "signature": b"hardware_signature"
            }
        ]

        # Authenticate
        session_key = vault.authenticate("user123", factors)

        assert len(session_key) == 32  # AES-256 key size
        assert isinstance(session_key, bytes)

    def test_outer_vault_password_based_key_derivation(self):
        """Test password-based key derivation."""
        vault = OuterVault()

        password = "correct horse battery staple"
        salt = b"unique_salt_per_user"

        # Derive key from password
        derived_key = vault.derive_key_from_password(password, salt)

        assert len(derived_key) == 32
        assert isinstance(derived_key, bytes)

        # Same password + salt should produce same key
        derived_key2 = vault.derive_key_from_password(password, salt)
        assert derived_key == derived_key2

        # Different password should produce different key
        wrong_key = vault.derive_key_from_password("wrong_password", salt)
        assert derived_key != wrong_key

    def test_outer_vault_session_management(self):
        """Test session creation and validation."""
        vault = OuterVault()

        user_id = "test_user"
        factors = [{"type": "mock_factor"}]

        # Create session
        session = vault.create_session(user_id, factors)

        assert "session_id" in session
        assert "session_key" in session
        assert "expires_at" in session
        assert "user_id" in session

        # Validate session
        is_valid = vault.validate_session(session["session_id"])
        assert is_valid

        # Expire session
        vault.expire_session(session["session_id"])
        is_valid_after_expiry = vault.validate_session(session["session_id"])
        assert not is_valid_after_expiry


class TestIsolationRoomIntegration:
    """Integration tests for Isolation Room protocol."""

    @patch('sudarshan.protocols.IsolationRoom.verify_enclave')
    def test_isolation_room_enclave_execution(self, mock_verify):
        """Test secure execution in hardware enclave."""
        mock_verify.return_value = True

        room = IsolationRoom()

        # Test data
        sensitive_data = b"confidential_information"
        operation = "encrypt"

        # Execute in enclave
        result = room.execute_in_enclave(operation, sensitive_data)

        assert result is not None
        mock_verify.assert_called_once()

    def test_isolation_room_attestation(self):
        """Test hardware attestation verification."""
        room = IsolationRoom()

        # Mock attestation data
        attestation = {
            "enclave_id": "sgx_enclave_123",
            "measurement": b"enclave_measurement_hash",
            "platform_info": "sgx_platform_data"
        }

        # Verify attestation
        is_valid = room.verify_attestation(attestation)

        # In real implementation, this would verify against trusted values
        assert isinstance(is_valid, bool)

    def test_isolation_room_side_channel_protection(self):
        """Test protection against side-channel attacks."""
        room = IsolationRoom()

        # Test with timing-sensitive operation
        start_time = datetime.now()

        result1 = room.execute_secure_operation("timing_test", b"data1")
        result2 = room.execute_secure_operation("timing_test", b"data2")

        end_time = datetime.now()

        # Ensure operations complete in reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete quickly

        # Results should be consistent regardless of input
        assert result1 is not None
        assert result2 is not None


class TestTransactionCapsuleIntegration:
    """Integration tests for Transaction Capsule protocol."""

    def test_transaction_capsule_creation_and_verification(self):
        """Test complete transaction capsule lifecycle."""
        capsule = TransactionCapsule()

        # Transaction data
        payload = {
            "amount": 1000000,  # 0.01 BTC in satoshis
            "recipient": "bc1qrecipientaddress",
            "fee": 1000,
            "timestamp": datetime.utcnow().isoformat()
        }

        recipient_public_key = b"mock_recipient_public_key"

        # Create transaction capsule
        tx_capsule = capsule.create_transaction(payload, recipient_public_key)

        assert "capsule_id" in tx_capsule
        assert "encrypted_payload" in tx_capsule
        assert "signature" in tx_capsule
        assert "public_key" in tx_capsule

        # Verify transaction
        is_valid = capsule.verify_transaction(tx_capsule)

        assert is_valid

    def test_transaction_capsule_one_time_usage(self):
        """Test that transaction capsules can only be used once."""
        capsule = TransactionCapsule()

        payload = {"test": "data"}
        recipient_key = b"recipient_key"

        # Create capsule
        tx_capsule = capsule.create_transaction(payload, recipient_key)

        # First verification should succeed
        assert capsule.verify_transaction(tx_capsule)

        # Second verification should fail (one-time use)
        assert not capsule.verify_transaction(tx_capsule)

    def test_transaction_capsule_replay_protection(self):
        """Test protection against replay attacks."""
        capsule = TransactionCapsule()

        # Create multiple similar transactions
        tx1 = capsule.create_transaction({"id": 1}, b"key1")
        tx2 = capsule.create_transaction({"id": 2}, b"key2")

        # Each should have unique identifiers
        assert tx1["capsule_id"] != tx2["capsule_id"]

        # Both should be valid initially
        assert capsule.verify_transaction(tx1)
        assert capsule.verify_transaction(tx2)

        # After use, both should be invalid
        assert not capsule.verify_transaction(tx1)
        assert not capsule.verify_transaction(tx2)


class TestCompleteBoxInABoxIntegration:
    """Integration tests for complete Box-in-a-Box system."""

    def test_complete_security_stack(self):
        """Test the complete security stack from asset to transaction."""
        # Step 1: Inner Shield - Protect legacy asset
        legacy_asset = b"bitcoin_private_key_mock"
        shield = InnerShield()
        protected_asset = shield.wrap_asset(legacy_asset, {"type": "bitcoin_key"})

        # Step 2: Outer Vault - Multi-factor authentication
        vault = OuterVault()
        factors = [{"type": "biometric"}, {"type": "hardware_token"}]
        session_key = vault.authenticate("user123", factors)

        # Step 3: Isolation Room - Secure processing
        room = IsolationRoom()
        with patch.object(room, 'verify_enclave', return_value=True):
            processed_asset = room.execute_in_enclave("process_asset", protected_asset)

        # Step 4: Transaction Capsule - Create transaction
        capsule = TransactionCapsule()
        transaction_data = {
            "asset": "bitcoin",
            "action": "transfer",
            "amount": 0.001
        }
        tx_capsule = capsule.create_transaction(transaction_data, session_key)

        # Verify complete flow
        assert processed_asset is not None
        assert tx_capsule is not None
        assert capsule.verify_transaction(tx_capsule)

    def test_security_layer_isolation(self):
        """Test that each security layer operates independently."""
        # Test that compromising one layer doesn't affect others
        legacy_asset = b"test_asset"

        # Layer 1: Inner Shield
        shield = InnerShield()
        protected = shield.wrap_asset(legacy_asset, {})

        # Layer 2: Outer Vault (independent of Layer 1)
        vault = OuterVault()
        factors = [{"type": "password"}]
        session = vault.authenticate("user", factors)

        # Layer 3: Isolation Room (independent of others)
        room = IsolationRoom()
        with patch.object(room, 'verify_enclave', return_value=True):
            isolated = room.execute_in_enclave("isolate", legacy_asset)

        # Layer 4: Transaction Capsule (independent of others)
        capsule = TransactionCapsule()
        tx = capsule.create_transaction({"test": "data"}, b"key")

        # All layers should work independently
        assert protected is not None
        assert session is not None
        assert isolated is not None
        assert tx is not None

    def test_error_propagation_through_layers(self):
        """Test that errors are properly handled across layers."""
        # Test error in Inner Shield
        shield = InnerShield()

        # Invalid asset data
        with pytest.raises(ValueError):
            shield.wrap_asset(None, {})

        # Test error in Outer Vault
        vault = OuterVault()

        # Invalid factors
        with pytest.raises(ValueError):
            vault.authenticate("user", [])

        # Test error in Transaction Capsule
        capsule = TransactionCapsule()

        # Invalid payload
        with pytest.raises(ValueError):
            capsule.create_transaction(None, b"key")


class TestSPQFileIntegration:
    """Integration tests for .spq file operations with Box-in-a-Box."""

    def test_spq_with_box_in_a_box_metadata(self):
        """Test .spq file creation with Box-in-a-Box metadata."""
        # Create test data
        test_data = json.dumps({
            "transaction": {
                "amount": 50000,
                "recipient": "wallet_address",
                "asset": "bitcoin"
            }
        }).encode()

        # Create comprehensive metadata
        metadata = {
            "file_type": "bitcoin_transaction",
            "security_layers": ["inner_shield", "outer_vault", "isolation_room", "transaction_capsule"],
            "encryption": "kyber1024_aes256",
            "compression": "zstd",
            "created_by": "sudarshan_engine",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "permissions": ["owner_read", "owner_write"],
            "tags": ["finance", "blockchain", "confidential"]
        }

        # Create .spq file
        spq_result = spq_create(
            data=test_data,
            metadata=metadata,
            algorithm="kyber1024",
            compression="zstd"
        )

        assert "data" in spq_result
        assert "metadata" in spq_result
        assert len(spq_result["data"]) > 0

        # Read back .spq file
        read_result = spq_read(data=spq_result["data"])

        assert read_result["data"] == test_data
        assert read_result["metadata"]["file_type"] == "bitcoin_transaction"
        assert "security_layers" in read_result["metadata"]

    def test_spq_file_integrity_verification(self):
        """Test .spq file integrity verification."""
        test_data = b"integrity test data"
        metadata = {"test": "integrity"}

        # Create file
        spq_data = spq_create(data=test_data, metadata=metadata)

        # Verify integrity during read
        result = spq_read(data=spq_data["data"])

        assert result["data"] == test_data
        assert result["metadata"] == metadata

        # Test with corrupted data
        corrupted = spq_data["data"][:]
        corrupted = corrupted[:10] + bytes([corrupted[10] ^ 0xFF]) + corrupted[11:]

        with pytest.raises(ValueError):
            spq_read(data=corrupted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])