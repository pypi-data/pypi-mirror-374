"""
Sudarshan Engine - Core Cryptographic Operations

This module provides the core encryption/decryption logic for the Sudarshan Engine,
integrating post-quantum cryptography (PQC) with traditional symmetric encryption.

Key Features:
- Kyber KEM for quantum-safe key exchange
- AES-256-GCM/ChaCha20-Poly1305 for symmetric encryption
- Dilithium/Falcon for digital signatures
- SHA3-512 for integrity hashing
- HKDF for key derivation
- Comprehensive error handling and security checks
"""

import secrets
import json
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

if TYPE_CHECKING:
    from bindings.oqs_bindings import OQSBindings, OQSAlgorithm

try:
    from bindings.oqs_bindings import OQSBindings, OQSAlgorithm, get_oqs_instance, OQSError
    oqs_available = True
except ImportError:
    # Fallback for when bindings are not available
    OQSBindings = type(None)  # type: ignore
    OQSAlgorithm = type(None)  # type: ignore
    get_oqs_instance = lambda: None  # type: ignore
    OQSError = Exception
    oqs_available = False


class CryptoError(Exception):
    """Base exception for cryptographic operations"""
    pass


class EncryptionError(CryptoError):
    """Raised when encryption fails"""
    pass


class DecryptionError(CryptoError):
    """Raised when decryption fails"""
    pass


class SignatureError(CryptoError):
    """Raised when signature operations fail"""
    pass


class KeyDerivationError(CryptoError):
    """Raised when key derivation fails"""
    pass


class SudarshanCrypto:
    """
    Core cryptographic operations for Sudarshan Engine

    Integrates PQC algorithms with traditional symmetric crypto
    """

    def __init__(self, oqs_bindings: Optional["OQSBindings"] = None):
        """
        Initialize crypto engine

        Args:
            oqs_bindings: OQS bindings instance (auto-created if None)
        """
        self.oqs: Optional["OQSBindings"]
        if oqs_bindings is not None:
            self.oqs = oqs_bindings
        elif oqs_available:
            self.oqs = get_oqs_instance()
        else:
            self.oqs = None

        self.oqs_available = self.oqs is not None

        # Default algorithms
        self.kem_algorithm: Optional["OQSAlgorithm"] = None
        self.signature_algorithm: Optional["OQSAlgorithm"] = None
        if oqs_available:
            self.kem_algorithm = OQSAlgorithm.KYBER1024
            self.signature_algorithm = OQSAlgorithm.DILITHIUM5
        self.symmetric_algorithm = "aes256gcm"  # or "chacha20poly1305"
        self.hash_algorithm = "sha3_512"


    # ============================================================================
    # Key Management
    # ============================================================================

    def generate_kem_keypair(self, algorithm: Optional["OQSAlgorithm"] = None) -> Tuple[bytes, bytes]:
        """
        Generate KEM keypair for quantum-safe key exchange

        Args:
            algorithm: KEM algorithm (default: Kyber1024)

        Returns:
            Tuple of (public_key, secret_key)
        """
        if not self.oqs_available or not self.oqs:
            raise KeyDerivationError("OQS not available")

        try:
            algo = algorithm or self.kem_algorithm
            if not algo:
                raise KeyDerivationError("KEM algorithm not specified and no default available.")
            return self.oqs.kyber_keypair(algo)
        except OQSError as e:
            raise KeyDerivationError(f"KEM keypair generation failed: {e}")

    def generate_signature_keypair(self, algorithm: Optional["OQSAlgorithm"] = None) -> Tuple[bytes, bytes]:
        """
        Generate signature keypair for authentication

        Args:
            algorithm: Signature algorithm (default: Dilithium5)

        Returns:
            Tuple of (public_key, secret_key)
        """
        if not self.oqs_available or not self.oqs:
            raise KeyDerivationError("OQS not available")

        try:
            algo = algorithm or self.signature_algorithm
            if not algo:
                raise KeyDerivationError("Signature algorithm not specified and no default available.")
            return self.oqs.dilithium_keypair(algo)
        except OQSError as e:
            raise KeyDerivationError(f"Signature keypair generation failed: {e}")

    # ============================================================================
    # Key Encapsulation/Exchange
    # ============================================================================

    def encapsulate_key(self, recipient_public_key: bytes,
                        algorithm: Optional["OQSAlgorithm"] = None) -> Tuple[bytes, bytes]:
        """
        Perform KEM encapsulation to establish shared secret

        Args:
            recipient_public_key: Recipient's KEM public key
            algorithm: KEM algorithm

        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        if not self.oqs_available or not self.oqs:
            raise KeyDerivationError("OQS not available")

        try:
            algo = algorithm or self.kem_algorithm
            if not algo:
                raise KeyDerivationError("KEM algorithm not specified and no default available.")
            return self.oqs.kyber_encapsulate(algo, recipient_public_key)
        except OQSError as e:
            raise KeyDerivationError(f"Key encapsulation failed: {e}")

    def decapsulate_key(self, ciphertext: bytes, recipient_secret_key: bytes,
                        algorithm: Optional["OQSAlgorithm"] = None) -> bytes:
        """
        Perform KEM decapsulation to recover shared secret

        Args:
            ciphertext: KEM ciphertext
            recipient_secret_key: Recipient's KEM secret key
            algorithm: KEM algorithm

        Returns:
            Shared secret
        """
        if not self.oqs_available or not self.oqs:
            raise KeyDerivationError("OQS not available")

        try:
            algo = algorithm or self.kem_algorithm
            if not algo:
                raise KeyDerivationError("KEM algorithm not specified and no default available.")
            return self.oqs.kyber_decapsulate(algo, ciphertext, recipient_secret_key)
        except OQSError as e:
            raise KeyDerivationError(f"Key decapsulation failed: {e}")

    # ============================================================================
    # Symmetric Encryption/Decryption
    # ============================================================================

    def encrypt_data(self, plaintext: bytes, key: bytes,
                    associated_data: Optional[bytes] = None) -> Dict[str, bytes]:
        """
        Encrypt data using authenticated symmetric encryption

        Args:
            plaintext: Data to encrypt
            key: Encryption key (32 bytes for AES-256)
            associated_data: Additional authenticated data

        Returns:
            Dict with 'ciphertext', 'nonce', 'tag'
        """
        # Input validation
        if not isinstance(plaintext, bytes):
            raise EncryptionError("Plaintext must be bytes")
        if not isinstance(key, bytes):
            raise EncryptionError("Key must be bytes")
        if len(key) != 32:
            raise EncryptionError("Key must be 32 bytes for AES-256/Chacha20")
        if len(plaintext) == 0:
            raise EncryptionError("Plaintext cannot be empty")
        if len(plaintext) > 2**32:  # 4GB limit
            raise EncryptionError("Plaintext too large (max 4GB)")
        if associated_data and len(associated_data) > 2**16:  # 64KB limit
            raise EncryptionError("Associated data too large (max 64KB)")

        try:
            if self.symmetric_algorithm == "aes256gcm":
                return self._encrypt_aes_gcm(plaintext, key, associated_data)
            elif self.symmetric_algorithm == "chacha20poly1305":
                return self._encrypt_chacha20_poly1305(plaintext, key, associated_data)
            else:
                raise EncryptionError(f"Unsupported symmetric algorithm: {self.symmetric_algorithm}")
        except Exception as e:
            raise EncryptionError(f"Symmetric encryption failed: {e}")

    def decrypt_data(self, ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes,
                    associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using authenticated symmetric decryption

        Args:
            ciphertext: Encrypted data
            key: Decryption key
            nonce: Initialization vector/nonce
            tag: Authentication tag
            associated_data: Additional authenticated data

        Returns:
            Decrypted plaintext
        """
        # Input validation
        if not isinstance(ciphertext, bytes):
            raise DecryptionError("Ciphertext must be bytes")
        if not isinstance(key, bytes):
            raise DecryptionError("Key must be bytes")
        if not isinstance(nonce, bytes):
            raise DecryptionError("Nonce must be bytes")
        if not isinstance(tag, bytes):
            raise DecryptionError("Tag must be bytes")

        if len(key) != 32:
            raise DecryptionError("Key must be 32 bytes for AES-256/Chacha20")
        if len(nonce) != 12:
            raise DecryptionError("Nonce must be 12 bytes")
        if len(ciphertext) == 0:
            raise DecryptionError("Ciphertext cannot be empty")
        if len(ciphertext) > 2**32:  # 4GB limit
            raise DecryptionError("Ciphertext too large (max 4GB)")
        if associated_data and len(associated_data) > 2**16:  # 64KB limit
            raise DecryptionError("Associated data too large (max 64KB)")

        try:
            if self.symmetric_algorithm == "aes256gcm":
                return self._decrypt_aes_gcm(ciphertext, key, nonce, tag, associated_data)
            elif self.symmetric_algorithm == "chacha20poly1305":
                return self._decrypt_chacha20_poly1305(ciphertext, key, nonce, tag, associated_data)
            else:
                raise DecryptionError(f"Unsupported symmetric algorithm: {self.symmetric_algorithm}")
        except Exception as e:
            raise DecryptionError(f"Symmetric decryption failed: {e}")

    def _encrypt_aes_gcm(self, plaintext: bytes, key: bytes,
                        associated_data: Optional[bytes] = None) -> Dict[str, bytes]:
        """AES-256-GCM encryption"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag

        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'tag': tag
        }

    def _decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes,
                        associated_data: Optional[bytes] = None) -> bytes:
        """AES-256-GCM decryption"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def _encrypt_chacha20_poly1305(self, plaintext: bytes, key: bytes,
                                  associated_data: Optional[bytes] = None) -> Dict[str, bytes]:
        """ChaCha20-Poly1305 encryption with proper AEAD construction"""
        if len(key) != 32:
            raise EncryptionError("ChaCha20-Poly1305 requires 32-byte key")

        nonce = secrets.token_bytes(12)  # 96-bit nonce for ChaCha20-Poly1305
        aead_cipher = ChaCha20Poly1305(key)

        # ChaCha20Poly1305 handles both encryption and authentication
        ciphertext = aead_cipher.encrypt(nonce, plaintext, associated_data or b"")

        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'tag': b''  # ChaCha20Poly1305 includes auth tag in ciphertext
        }

    def _decrypt_chacha20_poly1305(self, ciphertext: bytes, key: bytes, nonce: bytes, _tag: bytes,
                                  associated_data: Optional[bytes] = None) -> bytes:
        """ChaCha20-Poly1305 decryption with proper AEAD construction"""
        if len(key) != 32:
            raise DecryptionError("ChaCha20Poly1305 requires 32-byte key")

        aead_cipher = ChaCha20Poly1305(key)

        # ChaCha20Poly1305 handles both decryption and authentication
        # The tag is included in the ciphertext, so we ignore the tag parameter
        try:
            plaintext = aead_cipher.decrypt(nonce, ciphertext, associated_data or b"")
            return plaintext
        except InvalidTag:
            raise DecryptionError("Authentication tag verification failed")

    # ============================================================================
    # Digital Signatures
    # ============================================================================

    def sign_data(self, data: bytes, secret_key: bytes,
                  algorithm: Optional["OQSAlgorithm"] = None) -> bytes:
        """
        Sign data with PQC signature

        Args:
            data: Data to sign
            secret_key: Signer's secret key
            algorithm: Signature algorithm

        Returns:
            Digital signature
        """
        if not self.oqs_available or not self.oqs:
            raise SignatureError("OQS not available")

        try:
            algo = algorithm or self.signature_algorithm
            if not algo:
                raise SignatureError("Signature algorithm not specified and no default available.")
            return self.oqs.dilithium_sign(algo, data, secret_key)
        except OQSError as e:
            raise SignatureError(f"Data signing failed: {e}")

    def verify_signature(self, data: bytes, signature: bytes, public_key: bytes,
                         algorithm: Optional["OQSAlgorithm"] = None) -> bool:
        """
        Verify PQC signature

        Args:
            data: Original data
            signature: Digital signature
            public_key: Signer's public key
            algorithm: Signature algorithm

        Returns:
            True if signature is valid
        """
        if not self.oqs_available or not self.oqs:
            return False

        try:
            algo = algorithm or self.signature_algorithm
            if not algo:
                # If no algorithm, we can't verify.
                return False
            return self.oqs.dilithium_verify(algo, data, signature, public_key)
        except OQSError:
            return False

    # ============================================================================
    # Hashing and Key Derivation
    # ============================================================================

    def hash_data(self, data: bytes, algorithm: str = "sha3_512") -> bytes:
        """
        Hash data with quantum-resistant hash function

        Args:
            data: Data to hash
            algorithm: Hash algorithm

        Returns:
            Hash digest
        """
        # Input validation
        if not isinstance(data, bytes):
            raise CryptoError("Data must be bytes")
        if len(data) > 2**30:  # 1GB limit for hashing
            raise CryptoError("Data too large for hashing (max 1GB)")

        try:
            import hashlib
            if algorithm == "sha3_256":
                return hashlib.sha3_256(data).digest()
            elif algorithm == "sha3_512":
                return hashlib.sha3_512(data).digest()
            elif algorithm.startswith("shake"):
                # Extract output length from algorithm name (e.g., "shake128_32")
                parts = algorithm.split("_")
                if len(parts) == 2:
                    shake_type, output_len_str = parts
                    try:
                        output_len = int(output_len_str)
                        if output_len < 1 or output_len > 2**16:  # Reasonable limits
                            raise CryptoError(f"SHAKE output length out of range: {output_len}")
                        if shake_type == "shake128":
                            return hashlib.shake_128(data).digest(output_len)
                        elif shake_type == "shake256":
                            return hashlib.shake_256(data).digest(output_len)
                        else:
                            raise CryptoError(f"Unsupported SHAKE variant: {shake_type}")
                    except ValueError:
                        raise CryptoError(f"Invalid SHAKE output length: {output_len_str}")
                raise CryptoError(f"Invalid SHAKE parameters: {algorithm}")
            else:
                raise CryptoError(f"Unsupported hash algorithm: {algorithm}")
        except Exception as e:
            raise CryptoError(f"Hashing failed: {e}")

    def derive_key(self, shared_secret: bytes, salt: bytes, info: bytes,
                  key_length: int = 32) -> bytes:
        """
        Derive encryption key from shared secret using HKDF

        Args:
            shared_secret: PQC shared secret
            salt: Salt for key derivation
            info: Context information
            key_length: Desired key length

        Returns:
            Derived key
        """
        # Input validation
        if not isinstance(shared_secret, bytes):
            raise KeyDerivationError("Shared secret must be bytes")
        if not isinstance(salt, bytes):
            raise KeyDerivationError("Salt must be bytes")
        if not isinstance(info, bytes):
            raise KeyDerivationError("Info must be bytes")

        if len(shared_secret) < 16:
            raise KeyDerivationError("Shared secret too short (min 16 bytes)")
        if len(shared_secret) > 2**16:  # 64KB limit
            raise KeyDerivationError("Shared secret too large (max 64KB)")
        if len(salt) < 16:
            raise KeyDerivationError("Salt too short (min 16 bytes)")
        if len(salt) > 2**8:  # 256B limit
            raise KeyDerivationError("Salt too large (max 256 bytes)")
        if len(info) > 2**8:  # 256B limit
            raise KeyDerivationError("Info too large (max 256 bytes)")
        if key_length < 16 or key_length > 2**8:  # 16-256 bytes
            raise KeyDerivationError("Key length out of range (16-256 bytes)")

        try:
            hkdf = HKDF(
                algorithm=hashes.SHA3_512(),
                length=key_length,
                salt=salt,
                info=info,
                backend=default_backend()
            )
            return hkdf.derive(shared_secret)
        except Exception as e:
            raise KeyDerivationError(f"Key derivation failed: {e}")

    # ============================================================================
    # Complete Encryption/Decryption Workflow
    # ============================================================================

    def encrypt_payload(self, plaintext: bytes, recipient_kem_public_key: bytes,
                       sender_sig_secret_key: Optional[bytes] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete encryption workflow for .spq files

        Args:
            plaintext: Data to encrypt
            recipient_kem_public_key: Recipient's KEM public key
            sender_sig_secret_key: Sender's signature secret key (optional)
            metadata: Additional metadata

        Returns:
            Complete encryption result
        """
        # Step 1: KEM key exchange
        kem_ciphertext, shared_secret = self.encapsulate_key(recipient_kem_public_key)

        # Step 2: Key derivation
        salt = secrets.token_bytes(16)
        info = b"Sudarshan Engine Payload Encryption"
        encryption_key = self.derive_key(shared_secret, salt, info)

        # Step 3: Symmetric encryption
        associated_data = json.dumps(metadata or {}).encode() if metadata else None
        encrypted_data = self.encrypt_data(plaintext, encryption_key, associated_data)

        # Step 4: Integrity hash
        payload_to_hash = encrypted_data['ciphertext']
        integrity_hash = self.hash_data(payload_to_hash)

        # Step 5: Digital signature (optional)
        if sender_sig_secret_key:
            data_to_sign = integrity_hash
            signature = self.sign_data(data_to_sign, sender_sig_secret_key)
        else:
            signature = b""  # empty signature if signature not provided
        return {
            'kem_ciphertext': kem_ciphertext,
            'encrypted_payload': encrypted_data['ciphertext'],
            'payload_nonce': encrypted_data['nonce'],
            'payload_tag': encrypted_data['tag'],
            'salt': salt,
            'integrity_hash': integrity_hash,
            'signature': signature,
            'metadata': metadata
        }

    def decrypt_payload(self, encrypted_data: Dict[str, Any],
                       recipient_kem_secret_key: bytes,
                       sender_sig_public_key: Optional[bytes] = None) -> bytes:
        """
        Complete decryption workflow for .spq files

        Args:
            encrypted_data: Encrypted data structure
            recipient_kem_secret_key: Recipient's KEM secret key
            sender_sig_public_key: Sender's signature public key (optional)

        Returns:
            Decrypted plaintext
        """
        # Step 1: KEM key recovery
        shared_secret = self.decapsulate_key(
            encrypted_data['kem_ciphertext'],
            recipient_kem_secret_key
        )

        # Step 2: Key derivation
        salt = encrypted_data['salt']
        info = b"Sudarshan Engine Payload Encryption"
        encryption_key = self.derive_key(shared_secret, salt, info)

        # Step 3: Verify integrity hash
        computed_hash = self.hash_data(encrypted_data['encrypted_payload'])
        if computed_hash != encrypted_data['integrity_hash']:
            raise DecryptionError("Payload integrity check failed")

        # Step 4: Verify signature (optional)
        if sender_sig_public_key and encrypted_data.get('signature'):
            data_to_verify = encrypted_data['integrity_hash']
            signature = encrypted_data['signature']
            if not self.verify_signature(data_to_verify, signature, sender_sig_public_key):
                raise DecryptionError("Signature verification failed")

        # Step 5: Symmetric decryption
        associated_data = json.dumps(encrypted_data.get('metadata', {})).encode()
        plaintext = self.decrypt_data(
            encrypted_data['encrypted_payload'],
            encryption_key,
            encrypted_data['payload_nonce'],
            encrypted_data['payload_tag'],
            associated_data
        )

        return plaintext

    # ============================================================================
    # Utility Functions
    # ============================================================================

    def generate_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        if self.oqs_available:
            return self.oqs.random_bytes(length)
        else:
            # Fallback to Python's secrets module
            return secrets.token_bytes(length)

    def hash_sha3_512(self, data: bytes) -> bytes:
        """Hash data with SHA3-512"""
        return self.hash_data(data, "sha3_512")

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about configured algorithms"""
        info = {
            'symmetric_algorithm': self.symmetric_algorithm,
            'hash_algorithm': self.hash_algorithm,
            'oqs_available': self.oqs_available
        }

        if self.oqs_available and self.kem_algorithm:
            info['kem_algorithm'] = str(self.kem_algorithm)
        else:
            info['kem_algorithm'] = 'Not available'

        if self.oqs_available and self.signature_algorithm:
            info['signature_algorithm'] = str(self.signature_algorithm)
        else:
            info['signature_algorithm'] = 'Not available'

        if self.oqs_available and self.oqs:
            info['oqs_version'] = getattr(self.oqs, 'get_version', lambda: 'Unknown')()
        else:
            info['oqs_version'] = 'Not available'

        return info


# ============================================================================
# Standalone Functions for External Use
# ============================================================================

def generate_random_bytes(length: int) -> bytes:
    """Generate cryptographically secure random bytes (standalone function)"""
    engine = get_crypto_instance()
    return engine.generate_random_bytes(length)


def hash_sha3_512(data: bytes) -> bytes:
    """Hash data with SHA3-512 (standalone function)"""
    engine = get_crypto_instance()
    return engine.hash_sha3_512(data)

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about configured algorithms"""
        info = {
            'symmetric_algorithm': self.symmetric_algorithm,
            'hash_algorithm': self.hash_algorithm,
            'oqs_available': self.oqs_available
        }

        if self.oqs_available and self.kem_algorithm:
            info['kem_algorithm'] = self.kem_algorithm
        else:
            info['kem_algorithm'] = 'Not available'

        if self.oqs_available and self.signature_algorithm:
            info['signature_algorithm'] = self.signature_algorithm
        else:
            info['signature_algorithm'] = 'Not available'

        if self.oqs_available and self.oqs:
            info['oqs_version'] = self.oqs.get_version()
        else:
            info['oqs_version'] = 'Not available'

        return info


# ============================================================================
# Convenience Functions
# ============================================================================

def create_crypto_engine() -> SudarshanCrypto:
    """
    Create a configured Sudarshan crypto engine

    Returns:
        Configured crypto engine
    """
    return SudarshanCrypto()


def test_crypto_engine(engine: SudarshanCrypto) -> bool:
    """
    Test crypto engine functionality

    Args:
        engine: Crypto engine instance

    Returns:
        True if all tests pass
    """
    try:
        # Test symmetric encryption (always available)
        test_data = b"Hello, quantum world"
        key = engine.generate_random_bytes(32)
        encrypted = engine.encrypt_data(test_data, key)
        decrypted = engine.decrypt_data(
            encrypted['ciphertext'],
            key,
            encrypted['nonce'],
            encrypted['tag']
        )
        assert decrypted == test_data
        print("✓ Symmetric encryption works")

        # Test hashing (always available)
        hash_result = engine.hash_data(test_data)
        assert len(hash_result) == 64  # SHA3-512
        print("✓ Hashing works")

        # Test PQC operations only if available
        if engine.oqs_available:
            # Test KEM
            pub_key, sec_key = engine.generate_kem_keypair()
            ciphertext, shared_secret_1 = engine.encapsulate_key(pub_key)
            shared_secret_2 = engine.decapsulate_key(ciphertext, sec_key)
            assert shared_secret_1 == shared_secret_2
            print("✓ KEM operations work")

            # Test signatures
            sig_pub_key, sig_sec_key = engine.generate_signature_keypair()
            message = b"Test message for signing"
            signature = engine.sign_data(message, sig_sec_key)
            is_valid = engine.verify_signature(message, signature, sig_pub_key)
            assert is_valid
            print("✓ Digital signatures work")
        else:
            print("⚠️ PQC operations not available (OQS not loaded)")

        return True

    except Exception as e:
        print(f"✗ Crypto engine test failed: {e}")
        return False


# Global instance with thread safety
import threading
_crypto_instance: Optional[SudarshanCrypto] = None
_crypto_lock = threading.Lock()

def get_crypto_instance() -> SudarshanCrypto:
    """Get global crypto engine instance (thread-safe)"""
    global _crypto_instance
    if _crypto_instance is None:
        with _crypto_lock:
            # Double-check pattern to avoid race conditions
            if _crypto_instance is None:
                _crypto_instance = create_crypto_engine()
    return _crypto_instance


if __name__ == "__main__":
    # Test the crypto engine when run directly
    try:
        engine = create_crypto_engine()
        success = test_crypto_engine(engine)
        if success:
            print("\n🎉 All crypto engine tests passed!")
            print(f"Algorithm info: {engine.get_algorithm_info()}")
        else:
            print("\n❌ Some crypto engine tests failed!")
    except Exception as e:
        print(f"❌ Failed to create crypto engine: {e}")
        import traceback
        traceback.print_exc()