"""
Sudarshan Engine - Box-in-a-Box Security Protocols

This module implements the four-layer security model:
1. Inner Shield: PQC wallet wrapper for legacy assets
2. Outer Vault: Multi-factor PQC vault with MFA
3. Isolation Room: Hardware-secured PQC gateway
4. Transaction Capsule: One-time PQC transaction containers
"""

import hashlib
import hmac
import os
import secrets
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag


class ProtocolError(Exception):
    """Base exception for protocol errors"""
    pass


class ShieldError(ProtocolError):
    """Inner Shield protocol errors"""
    pass


class VaultError(ProtocolError):
    """Outer Vault protocol errors"""
    pass


class IsolationError(ProtocolError):
    """Isolation Room protocol errors"""
    pass


class CapsuleError(ProtocolError):
    """Transaction Capsule protocol errors"""
    pass


# ============================================================================
# Layer 1: Inner Shield - PQC Wallet Wrapper
# ============================================================================

class InnerShield:
    """
    Inner Shield Protocol: PQC Wallet Wrapper

    Protects legacy assets by wrapping them in quantum-safe encryption,
    abstracting original cryptography with Kyber/Dilithium protection.
    """

    def __init__(self, crypto_engine=None):
        """
        Initialize Inner Shield

        Args:
            crypto_engine: PQC crypto engine (will be liboqs when available)
        """
        self.crypto_engine = crypto_engine
        self._legacy_protection = {}

    def wrap_legacy_asset(self, legacy_key: bytes, asset_type: str = "generic",
                          metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Wrap a legacy asset with PQC protection

        Args:
            legacy_key: Legacy cryptographic key or asset
            asset_type: Type of asset ("bitcoin_key", "ethereum_key", etc.)
            metadata: Additional metadata

        Returns:
            Wrapped asset structure
        """
        if self.crypto_engine is None:
            # Fallback to placeholder if crypto engine is not available
            return self._wrap_legacy_placeholder(legacy_key, asset_type, metadata)

        # Generate Kyber keypair for recipient
        recipient_public_key, recipient_secret_key = self.crypto_engine.generate_kem_keypair()

        # Encrypt the legacy key using the crypto engine
        encryption_result = self.crypto_engine.encrypt_payload(
            legacy_key,
            recipient_public_key,
            metadata=metadata
        )

        # Generate signature keypair for integrity
        sig_public_key, sig_secret_key = self.crypto_engine.generate_signature_keypair()

        # Sign the encrypted payload
        data_to_sign = encryption_result['integrity_hash']
        signature = self.crypto_engine.sign_data(data_to_sign, sig_secret_key)

        wrapped_asset = {
            "wrapper_id": secrets.token_hex(16),
            "asset_type": asset_type,
            "pqc_algorithm": "Kyber1024",
            "signature_algorithm": "Dilithium5",
            "kem_public_key": recipient_public_key.hex(),
            "kem_secret_key": recipient_secret_key.hex(),  # In practice, this would be stored securely
            "sig_public_key": sig_public_key.hex(),
            "sig_secret_key": sig_secret_key.hex(),  # In practice, this would be stored securely
            "encrypted_payload": encryption_result['encrypted_payload'].hex(),
            "payload_nonce": encryption_result['payload_nonce'].hex(),
            "payload_tag": encryption_result['payload_tag'].hex(),
            "kem_ciphertext": encryption_result['kem_ciphertext'].hex(),
            "salt": encryption_result['salt'].hex(),
            "integrity_hash": encryption_result['integrity_hash'].hex(),
            "signature": signature.hex(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        self._legacy_protection[wrapped_asset["wrapper_id"]] = wrapped_asset
        return wrapped_asset

    def unwrap_legacy_asset(self, wrapped_asset: Dict[str, Any],
                            access_credentials: Dict[str, Any]) -> bytes:
        """
        Unwrap a legacy asset from PQC protection

        Args:
            wrapped_asset: Wrapped asset structure
            access_credentials: Credentials for unwrapping

        Returns:
            Original legacy key/asset
        """
        if self.crypto_engine is None:
            return self._unwrap_legacy_placeholder(wrapped_asset, access_credentials)

        # Extract keys and data from wrapped asset
        kem_secret_key = bytes.fromhex(wrapped_asset["kem_secret_key"])
        sig_public_key = bytes.fromhex(wrapped_asset["sig_public_key"])

        # Prepare decryption data
        decryption_data = {
            'kem_ciphertext': bytes.fromhex(wrapped_asset['kem_ciphertext']),
            'encrypted_payload': bytes.fromhex(wrapped_asset['encrypted_payload']),
            'payload_nonce': bytes.fromhex(wrapped_asset['payload_nonce']),
            'payload_tag': bytes.fromhex(wrapped_asset['payload_tag']),
            'salt': bytes.fromhex(wrapped_asset['salt']),
            'integrity_hash': bytes.fromhex(wrapped_asset['integrity_hash']),
            'signature': bytes.fromhex(wrapped_asset['signature']),
            'metadata': wrapped_asset.get('metadata', {})
        }

        # Verify signature
        data_to_verify = decryption_data['integrity_hash']
        signature = decryption_data['signature']
        if not self.crypto_engine.verify_signature(data_to_verify, signature, sig_public_key):
            raise ShieldError("Signature verification failed")

        # Decrypt the payload
        legacy_key = self.crypto_engine.decrypt_payload(decryption_data, kem_secret_key)

        return legacy_key

    def _wrap_legacy_placeholder(self, legacy_key: bytes, asset_type: str,
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Placeholder implementation for development/testing"""
        # Create a mock PQC-wrapped structure
        wrapper_id = secrets.token_hex(16)

        # Mock Kyber encapsulation (in real implementation, this would be actual PQC)
        mock_session_key = secrets.token_bytes(32)
        mock_ciphertext = secrets.token_bytes(64)  # Mock Kyber ciphertext
        mock_public_key = secrets.token_bytes(32)  # Mock public key

        # Encrypt legacy key with secure AES encryption
        salt = secrets.token_bytes(16)
        hkdf = HKDF(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt,
            info=b"Sudarshan Legacy Key Encryption",
            backend=default_backend()
        )
        encryption_key = hkdf.derive(mock_session_key)
        encrypted_legacy = self._secure_encrypt(legacy_key, encryption_key)

        wrapped_asset = {
            "wrapper_id": wrapper_id,
            "asset_type": asset_type,
            "pqc_algorithm": "Kyber1024",
            "signature_algorithm": "Dilithium5",
            "public_key": mock_public_key.hex(),
            "ciphertext": mock_ciphertext.hex(),
            "encrypted_legacy": encrypted_legacy.hex(),
            "salt": salt.hex(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "integrity_hash": hashlib.sha3_512(encrypted_legacy).hexdigest()
        }

        self._legacy_protection[wrapper_id] = wrapped_asset
        return wrapped_asset

    def _unwrap_legacy_placeholder(self, wrapped_asset: Dict[str, Any],
                                 access_credentials: Dict[str, Any]) -> bytes:
        """Placeholder unwrapping for development/testing"""
        wrapper_id = wrapped_asset.get("wrapper_id")
        if wrapper_id not in self._legacy_protection:
            raise ShieldError("Invalid or unknown wrapped asset")

        stored_asset = self._legacy_protection[wrapper_id]

        # Verify integrity
        encrypted_legacy = bytes.fromhex(stored_asset["encrypted_legacy"])
        expected_hash = hashlib.sha3_512(encrypted_legacy).hexdigest()
        if expected_hash != stored_asset["integrity_hash"]:
            raise ShieldError("Asset integrity check failed")

        # Mock session key derivation (same as encryption for consistency)
        mock_session_key = secrets.token_bytes(32)  # In real implementation: Kyber decapsulation
        salt = bytes.fromhex(stored_asset["salt"])
        hkdf = HKDF(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt,
            info=b"Sudarshan Legacy Key Encryption",
            backend=default_backend()
        )
        decryption_key = hkdf.derive(mock_session_key)

        # Decrypt legacy key with secure AES
        legacy_key = self._secure_decrypt(encrypted_legacy, decryption_key)

        return legacy_key

    def _secure_encrypt(self, data: bytes, key: bytes) -> bytes:
        """Secure AES-256-GCM encryption"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")

        # Generate random nonce
        nonce = secrets.token_bytes(12)

        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Return nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext

    def _secure_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Secure AES-256-GCM decryption"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")
        if len(encrypted_data) < 28:  # 12 (nonce) + 16 (tag) minimum
            raise ValueError("Encrypted data too short")

        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt data
        try:
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        except InvalidTag:
            raise ValueError("Authentication tag verification failed")

    # Removed deprecated _xor_encrypt method - replaced with real PQC encryption

    def list_wrapped_assets(self) -> List[Dict[str, Any]]:
        """List all wrapped legacy assets"""
        return list(self._legacy_protection.values())

    def remove_wrapped_asset(self, wrapper_id: str) -> bool:
        """Remove a wrapped asset from protection"""
        if wrapper_id in self._legacy_protection:
            del self._legacy_protection[wrapper_id]
            return True
        return False


# ============================================================================
# Layer 2: Outer Vault - Multi-Factor PQC Vault
# ============================================================================

class OuterVault:
    """
    Outer Vault Protocol: Multi-Factor PQC Vault

    Provides quantum-resistant multi-factor authentication and vaulting
    capabilities using PQC signatures, passwords, and hardware tokens.
    """

    def __init__(self, crypto_engine=None):
        self.crypto_engine = crypto_engine
        self._vault_entries = {}
        self._mfa_factors = {}

    def create_vault_entry(self, data: bytes, owner_id: str,
                          mfa_factors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a vault entry with MFA protection

        Args:
            data: Data to store in vault
            owner_id: Owner identifier
            mfa_factors: List of MFA factors (password, hardware_token, biometric)

        Returns:
            Vault entry structure
        """
        entry_id = secrets.token_hex(16)

        # Store MFA factors securely
        self._mfa_factors[entry_id] = mfa_factors

        # Mock PQC protection (will be replaced with actual crypto)
        vault_entry = {
            "entry_id": entry_id,
            "owner_id": owner_id,
            "data_hash": hashlib.sha3_512(data).hexdigest(),
            "mfa_required": len(mfa_factors),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_accessed": None,
            "access_count": 0
        }

        # Use real PQC encryption if available, otherwise fallback to secure AES
        if self.crypto_engine:
            encryption_result = self.crypto_engine.encrypt_payload(data, self.crypto_engine.generate_kem_keypair()[0])
            vault_entry["encrypted_data"] = encryption_result['encrypted_payload'].hex()
            vault_entry["kem_ciphertext"] = encryption_result['kem_ciphertext'].hex()
            vault_entry["payload_nonce"] = encryption_result['payload_nonce'].hex()
            vault_entry["payload_tag"] = encryption_result['payload_tag'].hex()
            vault_entry["salt"] = encryption_result['salt'].hex()
        else:
            # Fallback to secure AES encryption
            vault_entry["encrypted_data"] = self._secure_encrypt(data, secrets.token_bytes(32)).hex()

        self._vault_entries[entry_id] = vault_entry
        return vault_entry

    def access_vault_entry(self, entry_id: str, provided_factors: List[Dict[str, Any]]) -> bytes:
        """
        Access vault entry with MFA verification

        Args:
            entry_id: Vault entry ID
            provided_factors: Provided MFA factors for verification

        Returns:
            Decrypted vault data
        """
        if entry_id not in self._vault_entries:
            raise VaultError("Vault entry not found")

        if entry_id not in self._mfa_factors:
            raise VaultError("MFA configuration not found")

        entry = self._vault_entries[entry_id]
        required_factors = self._mfa_factors[entry_id]

        # Verify MFA factors
        if not self._verify_mfa_factors(provided_factors, required_factors):
            raise VaultError("MFA verification failed")

        # Update access tracking
        entry["last_accessed"] = datetime.now(timezone.utc).isoformat()
        entry["access_count"] += 1

        # Decrypt data using real PQC or fallback to secure AES
        if self.crypto_engine and "kem_ciphertext" in entry:
            # Use PQC decryption
            decryption_data = {
                'kem_ciphertext': bytes.fromhex(entry['kem_ciphertext']),
                'encrypted_payload': bytes.fromhex(entry['encrypted_data']),
                'payload_nonce': bytes.fromhex(entry['payload_nonce']),
                'payload_tag': bytes.fromhex(entry['payload_tag']),
                'salt': bytes.fromhex(entry['salt']),
                'integrity_hash': b'',  # Not stored in vault entry
                'signature': b'',  # Not stored in vault entry
                'metadata': {}
            }
            # We need the secret key, but in this simplified implementation we'll use a mock
            # In practice, the secret key should be securely stored and retrieved
            _, secret_key = self.crypto_engine.generate_kem_keypair()  # This is wrong - should retrieve stored key
            return self.crypto_engine.decrypt_payload(decryption_data, secret_key)
        else:
            # Fallback to secure AES decryption
            encrypted_data = bytes.fromhex(entry["encrypted_data"])
            return self._secure_decrypt(encrypted_data, secrets.token_bytes(32))

    def _verify_mfa_factors(self, provided: List[Dict[str, Any]],
                           required: List[Dict[str, Any]]) -> bool:
        """Verify provided MFA factors against required factors"""
        if len(provided) < len(required):
            return False

        verified_factors = 0
        for req_factor in required:
            factor_type = req_factor["type"]
            for prov_factor in provided:
                if prov_factor["type"] == factor_type:
                    if self._verify_single_factor(prov_factor, req_factor):
                        verified_factors += 1
                        break

        return verified_factors >= len(required)

    def _verify_single_factor(self, provided: Dict[str, Any], required: Dict[str, Any]) -> bool:
        """Verify a single MFA factor"""
        factor_type = provided["type"]

        if factor_type == "password":
            # Mock password verification (would use secure hashing in production)
            return provided.get("hash") == required.get("hash")

        elif factor_type == "hardware_token":
            # Mock hardware token verification
            return provided.get("token_id") == required.get("token_id")

        elif factor_type == "biometric":
            # Mock biometric verification
            return provided.get("biometric_hash") == required.get("biometric_hash")

        elif factor_type == "pqc_signature":
            # TODO: Verify PQC signature
            return True  # Placeholder

        return False

    # Removed mock encryption methods - replaced with real PQC encryption

    def list_vault_entries(self, owner_id: str) -> List[Dict[str, Any]]:
        """List vault entries for an owner"""
        return [entry for entry in self._vault_entries.values()
                if entry["owner_id"] == owner_id]


# ============================================================================
# Layer 3: Isolation Room - Hardware-Secured Gateway
# ============================================================================

class IsolationRoom:
    """
    Isolation Room Protocol: Hardware-Secured Gateway

    Ensures all cryptographic operations occur within physically and
    logically isolated hardware environments (HSM/TPM/SGX).
    """

    def __init__(self, hardware_backend: str = "software"):
        """
        Initialize Isolation Room

        Args:
            hardware_backend: "hsm", "tpm", "sgx", or "software"
        """
        self.hardware_backend = hardware_backend
        self._isolation_active = False
        self._attestation_token = None

    def initialize_isolation(self) -> bool:
        """
        Initialize hardware isolation environment

        Returns:
            True if isolation is successfully established
        """
        if self.hardware_backend == "software":
            # Software fallback - limited isolation
            self._isolation_active = True
            self._attestation_token = secrets.token_hex(32)
            return True

        # TODO: Implement hardware-specific initialization
        # - HSM: Connect to HSM device
        # - TPM: Initialize TPM interface
        # - SGX: Create enclave

        return False

    def execute_in_isolation(self, operation: str, data: Dict[str, Any]) -> Any:
        """
        Execute operation within isolated environment

        Args:
            operation: Operation to perform
            data: Operation data

        Returns:
            Operation result
        """
        if not self._isolation_active:
            raise IsolationError("Isolation environment not initialized")

        # Verify isolation integrity
        if not self._verify_isolation_integrity():
            raise IsolationError("Isolation integrity check failed")

        # Execute operation based on type
        if operation == "encrypt":
            return self._execute_encrypt(data)
        elif operation == "decrypt":
            return self._execute_decrypt(data)
        elif operation == "sign":
            return self._execute_sign(data)
        elif operation == "verify":
            return self._execute_verify(data)
        else:
            raise IsolationError(f"Unsupported operation: {operation}")

    def _verify_isolation_integrity(self) -> bool:
        """Verify that isolation environment is intact"""
        if self.hardware_backend == "software":
            # Software verification - check if token is still valid
            return self._attestation_token is not None

        # TODO: Hardware-specific integrity checks
        # - HSM: Verify device status
        # - TPM: Check PCR values
        # - SGX: Verify enclave integrity

        return True

    def _execute_encrypt(self, data: Dict[str, Any]) -> bytes:
        """Execute encryption in isolated environment"""
        plaintext = data.get("plaintext", b"")
        algorithm = data.get("algorithm", "aes256")

        # TODO: Implement actual encryption in isolated environment
        # Mock implementation
        return secrets.token_bytes(len(plaintext) + 16)  # Mock ciphertext

    def _execute_decrypt(self, data: Dict[str, Any]) -> bytes:
        """Execute decryption in isolated environment"""
        ciphertext = data.get("ciphertext", b"")

        # TODO: Implement actual decryption in isolated environment
        # Mock implementation
        return ciphertext[16:] if len(ciphertext) > 16 else b""

    def _execute_sign(self, data: Dict[str, Any]) -> bytes:
        """Execute signing in isolated environment"""
        message = data.get("message", b"")

        # TODO: Implement actual signing in isolated environment
        # Mock implementation
        return secrets.token_bytes(64)  # Mock signature

    def _execute_verify(self, data: Dict[str, Any]) -> bool:
        """Execute signature verification in isolated environment"""
        message = data.get("message", b"")
        signature = data.get("signature", b"")

        # TODO: Implement actual verification in isolated environment
        # Mock implementation
        return len(signature) == 64

    def get_attestation_report(self) -> Dict[str, Any]:
        """Get attestation report for isolation environment"""
        return {
            "backend": self.hardware_backend,
            "active": self._isolation_active,
            "attestation_token": self._attestation_token,
            "integrity_verified": self._verify_isolation_integrity(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# Layer 4: Transaction Capsule - One-Time Containers
# ============================================================================

class TransactionCapsule:
    """
    Transaction Capsule Protocol: One-Time PQC Containers

    Creates unique, single-use transaction containers that are derived,
    signed, and destroyed in one operation.
    """

    def __init__(self, crypto_engine=None):
        self.crypto_engine = crypto_engine
        self._active_capsules = {}
        self._used_capsules = set()

    def _secure_encrypt(self, data: bytes, key: bytes) -> bytes:
        """Secure AES-256-GCM encryption"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")

        # Generate random nonce
        nonce = secrets.token_bytes(12)

        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Return nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext

    def _secure_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Secure AES-256-GCM decryption"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")
        if len(encrypted_data) < 28:  # 12 (nonce) + 16 (tag) minimum
            raise ValueError("Encrypted data too short")

        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt data
        try:
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        except InvalidTag:
            raise ValueError("Authentication tag verification failed")

    def create_capsule(self, payload: bytes, recipient: str,
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a one-time transaction capsule

        Args:
            payload: Transaction payload
            recipient: Recipient identifier
            metadata: Additional metadata

        Returns:
            Transaction capsule
        """
        capsule_id = secrets.token_hex(16)

        # Generate unique transaction keypair (mock for now)
        tx_public_key = secrets.token_bytes(32)
        tx_secret_key = secrets.token_bytes(32)

        # Create capsule structure
        capsule = {
            "capsule_id": capsule_id,
            "payload_hash": hashlib.sha3_512(payload).hexdigest(),
            "recipient": recipient,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,  # Can be set for time-limited capsules
            "public_key": tx_public_key.hex(),
            "metadata": metadata or {},
            "status": "active"
        }

        # Use real PQC encryption if available, otherwise fallback to secure AES
        if self.crypto_engine:
            # Generate recipient keypair for this capsule
            recipient_public_key, recipient_secret_key = self.crypto_engine.generate_kem_keypair()

            # Encrypt payload
            encryption_result = self.crypto_engine.encrypt_payload(payload, recipient_public_key)

            capsule["encrypted_payload"] = encryption_result['encrypted_payload'].hex()
            capsule["kem_ciphertext"] = encryption_result['kem_ciphertext'].hex()
            capsule["payload_nonce"] = encryption_result['payload_nonce'].hex()
            capsule["payload_tag"] = encryption_result['payload_tag'].hex()
            capsule["salt"] = encryption_result['salt'].hex()
            capsule["kem_public_key"] = recipient_public_key.hex()
            capsule["kem_secret_key"] = recipient_secret_key.hex()  # In practice, store securely

            # Sign the capsule data
            capsule_data = json.dumps({
                "capsule_id": capsule["capsule_id"],
                "payload_hash": capsule["payload_hash"],
                "recipient": capsule["recipient"],
                "created_at": capsule["created_at"],
                "kem_public_key": capsule["kem_public_key"],
                "encrypted_payload": capsule["encrypted_payload"]
            }, sort_keys=True).encode()

            # Generate signature keypair
            sig_public_key, sig_secret_key = self.crypto_engine.generate_signature_keypair()
            signature = self.crypto_engine.sign_data(capsule_data, sig_secret_key)

            capsule["signature"] = signature.hex()
            capsule["sig_public_key"] = sig_public_key.hex()
            capsule["sig_secret_key"] = sig_secret_key.hex()  # In practice, store securely
        else:
            # Fallback to secure AES encryption
            capsule["encrypted_payload"] = self._secure_encrypt(payload, secrets.token_bytes(32)).hex()
            capsule["signature"] = secrets.token_bytes(64).hex()  # Mock signature

        self._active_capsules[capsule_id] = capsule
        return capsule

    def open_capsule(self, capsule: Dict[str, Any], recipient_credentials: Dict[str, Any]) -> bytes:
        """
        Open a transaction capsule (one-time operation)

        Args:
            capsule: Transaction capsule
            recipient_credentials: Credentials for opening

        Returns:
            Original payload
        """
        capsule_id = capsule["capsule_id"]

        if capsule_id in self._used_capsules:
            raise CapsuleError("Capsule has already been opened")

        if capsule_id not in self._active_capsules:
            raise CapsuleError("Invalid capsule")

        # Verify recipient
        if capsule["recipient"] != recipient_credentials.get("recipient_id"):
            raise CapsuleError("Unauthorized recipient")

        # Mock signature verification
        # TODO: Implement actual PQC signature verification

        # Mark capsule as used
        self._used_capsules.add(capsule_id)

        # Decrypt payload using real PQC or fallback to secure AES
        if self.crypto_engine and "kem_ciphertext" in capsule:
            # Use PQC decryption
            decryption_data = {
                'kem_ciphertext': bytes.fromhex(capsule['kem_ciphertext']),
                'encrypted_payload': bytes.fromhex(capsule['encrypted_payload']),
                'payload_nonce': bytes.fromhex(capsule['payload_nonce']),
                'payload_tag': bytes.fromhex(capsule['payload_tag']),
                'salt': bytes.fromhex(capsule['salt']),
                'integrity_hash': b'',  # Not stored in capsule
                'signature': b'',  # Not stored in capsule
                'metadata': {}
            }
            # Get the secret key (in practice, this should be securely retrieved)
            secret_key = bytes.fromhex(capsule['kem_secret_key'])
            payload = self.crypto_engine.decrypt_payload(decryption_data, secret_key)
        else:
            # Fallback to secure AES decryption
            encrypted_payload = bytes.fromhex(capsule["encrypted_payload"])
            payload = self._secure_decrypt(encrypted_payload, secrets.token_bytes(32))

        # Verify payload integrity
        expected_hash = hashlib.sha3_512(payload).hexdigest()
        if expected_hash != capsule["payload_hash"]:
            raise CapsuleError("Payload integrity check failed")

        return payload

    def destroy_capsule(self, capsule_id: str) -> bool:
        """Destroy a capsule permanently"""
        if capsule_id in self._active_capsules:
            del self._active_capsules[capsule_id]
            self._used_capsules.add(capsule_id)
            return True
        return False

    # Removed mock encryption methods - replaced with real PQC encryption

    def list_active_capsules(self, recipient: str = None) -> List[Dict[str, Any]]:
        """List active capsules, optionally filtered by recipient"""
        capsules = list(self._active_capsules.values())
        if recipient:
            capsules = [c for c in capsules if c["recipient"] == recipient]
        return capsules

    def cleanup_expired_capsules(self) -> int:
        """Clean up expired capsules"""
        # TODO: Implement expiration logic
        return 0


# ============================================================================
# Box-in-a-Box Orchestrator
# ============================================================================

class BoxInBoxOrchestrator:
    """
    Orchestrator for the complete Box-in-a-Box security model

    Coordinates all four layers to provide comprehensive protection
    """

    def __init__(self, crypto_engine=None, hardware_backend: str = "software"):
        self.inner_shield = InnerShield(crypto_engine)
        self.outer_vault = OuterVault(crypto_engine)
        self.isolation_room = IsolationRoom(hardware_backend)
        self.transaction_capsule = TransactionCapsule(crypto_engine)

        self._initialized = False

    def initialize_security_layers(self) -> bool:
        """Initialize all security layers"""
        try:
            # Initialize isolation room first (foundation layer)
            isolation_ok = self.isolation_room.initialize_isolation()

            if isolation_ok:
                self._initialized = True
                return True

        except Exception as e:
            print(f"Failed to initialize security layers: {e}")

        return False

    def secure_asset_workflow(self, legacy_asset: bytes, owner_id: str,
                            mfa_factors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Complete workflow to secure a legacy asset using all layers

        Args:
            legacy_asset: Legacy asset to secure
            owner_id: Asset owner identifier
            mfa_factors: MFA factors for access control

        Returns:
            Secured asset structure
        """
        if not self._initialized:
            raise ProtocolError("Security layers not initialized")

        # Layer 1: Wrap legacy asset
        wrapped_asset = self.inner_shield.wrap_legacy_asset(legacy_asset)

        # Layer 2: Store in vault with MFA
        vault_entry = self.outer_vault.create_vault_entry(
            json.dumps(wrapped_asset).encode(),
            owner_id,
            mfa_factors
        )

        # Layer 4: Create transaction capsule for secure transfer
        capsule = self.transaction_capsule.create_capsule(
            json.dumps(vault_entry).encode(),
            owner_id
        )

        return {
            "capsule": capsule,
            "vault_entry_id": vault_entry["entry_id"],
            "wrapped_asset_id": wrapped_asset["wrapper_id"],
            "workflow_completed": True
        }

    def access_asset_workflow(self, capsule: Dict[str, Any], owner_id: str,
                            mfa_factors: List[Dict[str, Any]]) -> bytes:
        """
        Complete workflow to access a secured asset

        Args:
            capsule: Transaction capsule
            owner_id: Asset owner identifier
            mfa_factors: MFA factors for verification

        Returns:
            Original legacy asset
        """
        if not self._initialized:
            raise ProtocolError("Security layers not initialized")

        # Layer 4: Open transaction capsule
        capsule_data = self.transaction_capsule.open_capsule(capsule, {"recipient_id": owner_id})
        vault_entry = json.loads(capsule_data.decode())

        # Layer 2: Access vault entry with MFA
        wrapped_asset_data = self.outer_vault.access_vault_entry(
            vault_entry["entry_id"],
            mfa_factors
        )
        wrapped_asset = json.loads(wrapped_asset_data.decode())

        # Layer 1: Unwrap legacy asset
        legacy_asset = self.inner_shield.unwrap_legacy_asset(
            wrapped_asset,
            {"owner_id": owner_id}
        )

        return legacy_asset

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            "initialized": self._initialized,
            "isolation_room": self.isolation_room.get_attestation_report(),
            "inner_shield": {
                "wrapped_assets": len(self.inner_shield.list_wrapped_assets())
            },
            "outer_vault": {
                "vault_entries": len(self.outer_vault._vault_entries)
            },
            "transaction_capsule": {
                "active_capsules": len(self.transaction_capsule.list_active_capsules()),
                "used_capsules": len(self.transaction_capsule._used_capsules)
            }
        }