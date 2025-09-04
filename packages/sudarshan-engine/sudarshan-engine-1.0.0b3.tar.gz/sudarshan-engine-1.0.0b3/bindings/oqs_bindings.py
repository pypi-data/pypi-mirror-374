"""
Sudarshan Engine - liboqs ctypes Bindings

This module provides Python ctypes bindings for the liboqs C library,
enabling access to post-quantum cryptographic algorithms from Python.

Supported Algorithms:
- Kyber (KEM): Kyber512, Kyber768, Kyber1024
- Dilithium (Signature): Dilithium2, Dilithium3, Dilithium5
- Falcon (Signature): Falcon-512, Falcon-1024
- SHA3/SHAKE: SHA3-256, SHA3-512, SHAKE128, SHAKE256
"""

import ctypes
import os
from typing import Optional, Tuple, Any
from enum import IntEnum


class OQSError(Exception):
    """Exception raised for liboqs errors"""
    pass


class OQSAlgorithm(IntEnum):
    """Supported PQC algorithms"""
    KYBER512 = 0
    KYBER768 = 1
    KYBER1024 = 2
    DILITHIUM2 = 3
    DILITHIUM3 = 4
    DILITHIUM5 = 5
    FALCON512 = 6
    FALCON1024 = 7


class OQSBindings:
    """
    ctypes bindings for liboqs library
    """

    def __init__(self, lib_path: str = "/usr/local/lib/liboqs.so"):
        """
        Initialize liboqs bindings

        Args:
            lib_path: Path to liboqs shared library
        """
        try:
            self.lib = ctypes.CDLL(lib_path)
            self._setup_function_signatures()
            print(f"Successfully loaded liboqs from {lib_path}")
        except OSError as e:
            raise OQSError(f"Failed to load liboqs library: {e}")

    def _setup_function_signatures(self):
        """Set up ctypes function signatures for liboqs functions"""

        # ============================================================================
        # Generic OQS Functions
        # ============================================================================

        # OQS_version
        self.lib.OQS_version.restype = ctypes.c_char_p

        # OQS_randombytes
        self.lib.OQS_randombytes.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint8)]
        self.lib.OQS_randombytes.restype = None

        # ============================================================================
        # Kyber KEM Functions
        # ============================================================================

        # Kyber512
        self.lib.OQS_KEM_kyber_512_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # public_key
            ctypes.POINTER(ctypes.c_uint8)   # secret_key
        ]
        self.lib.OQS_KEM_kyber_512_keypair.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_512_encaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # ciphertext
            ctypes.POINTER(ctypes.c_uint8),  # shared_secret
            ctypes.POINTER(ctypes.c_uint8)   # public_key
        ]
        self.lib.OQS_KEM_kyber_512_encaps.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_512_decaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # shared_secret
            ctypes.POINTER(ctypes.c_uint8),  # ciphertext
            ctypes.POINTER(ctypes.c_uint8)   # secret_key
        ]
        self.lib.OQS_KEM_kyber_512_decaps.restype = ctypes.c_int

        # Kyber768
        self.lib.OQS_KEM_kyber_768_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_768_keypair.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_768_encaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_768_encaps.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_768_decaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_768_decaps.restype = ctypes.c_int

        # Kyber1024
        self.lib.OQS_KEM_kyber_1024_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_1024_keypair.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_1024_encaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_1024_encaps.restype = ctypes.c_int

        self.lib.OQS_KEM_kyber_1024_decaps.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_KEM_kyber_1024_decaps.restype = ctypes.c_int

        # ============================================================================
        # Dilithium Signature Functions
        # ============================================================================

        # Dilithium2
        self.lib.OQS_SIG_dilithium_2_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_2_keypair.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_2_sign.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # signature
            ctypes.POINTER(ctypes.c_size_t), # signature_len
            ctypes.POINTER(ctypes.c_uint8),  # message
            ctypes.c_size_t,                 # message_len
            ctypes.POINTER(ctypes.c_uint8)   # secret_key
        ]
        self.lib.OQS_SIG_dilithium_2_sign.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_2_verify.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # message
            ctypes.c_size_t,                 # message_len
            ctypes.POINTER(ctypes.c_uint8),  # signature
            ctypes.c_size_t,                 # signature_len
            ctypes.POINTER(ctypes.c_uint8)   # public_key
        ]
        self.lib.OQS_SIG_dilithium_2_verify.restype = ctypes.c_int

        # Dilithium3
        self.lib.OQS_SIG_dilithium_3_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_3_keypair.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_3_sign.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_3_sign.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_3_verify.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_3_verify.restype = ctypes.c_int

        # Dilithium5
        self.lib.OQS_SIG_dilithium_5_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_5_keypair.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_5_sign.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_5_sign.restype = ctypes.c_int

        self.lib.OQS_SIG_dilithium_5_verify.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.OQS_SIG_dilithium_5_verify.restype = ctypes.c_int

        # ============================================================================
        # SHA3/SHAKE Functions (Note: Not available in this liboqs build)
        # ============================================================================
        # SHA3 functions are not available in the current liboqs installation
        # We'll use Python's hashlib instead for compatibility

    # ============================================================================
    # High-Level API Methods
    # ============================================================================

    def get_version(self) -> str:
        """Get liboqs version"""
        version = self.lib.OQS_version()
        return version.decode('utf-8') if version else "unknown"

    def random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        buffer = (ctypes.c_uint8 * length)()
        self.lib.OQS_randombytes(length, buffer)
        return bytes(buffer)

    # ============================================================================
    # Kyber KEM Methods
    # ============================================================================

    def kyber_keypair(self, algorithm: OQSAlgorithm) -> Tuple[bytes, bytes]:
        """
        Generate Kyber keypair

        Args:
            algorithm: Kyber variant (KYBER512, KYBER768, KYBER1024)

        Returns:
            Tuple of (public_key, secret_key)
        """
        if algorithm not in [OQSAlgorithm.KYBER512, OQSAlgorithm.KYBER768, OQSAlgorithm.KYBER1024]:
            raise OQSError(f"Unsupported Kyber algorithm: {algorithm}")

        # Key sizes for different Kyber variants
        key_sizes = {
            OQSAlgorithm.KYBER512: (800, 1632),
            OQSAlgorithm.KYBER768: (1184, 2400),
            OQSAlgorithm.KYBER1024: (1568, 3168)
        }

        public_key_size, secret_key_size = key_sizes[algorithm]

        public_key = (ctypes.c_uint8 * public_key_size)()
        secret_key = (ctypes.c_uint8 * secret_key_size)()

        # Call appropriate keypair function
        kyber_names = {
            OQSAlgorithm.KYBER512: "512",
            OQSAlgorithm.KYBER768: "768",
            OQSAlgorithm.KYBER1024: "1024"
        }
        func_name = f"OQS_KEM_kyber_{kyber_names[algorithm]}_keypair"
        func = getattr(self.lib, func_name)
        result = func(public_key, secret_key)

        if result != 0:
            raise OQSError(f"Kyber keypair generation failed: {result}")

        return bytes(public_key), bytes(secret_key)

    def kyber_encapsulate(self, algorithm: OQSAlgorithm, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Kyber encapsulation

        Args:
            algorithm: Kyber variant
            public_key: Recipient's public key

        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        if algorithm not in [OQSAlgorithm.KYBER512, OQSAlgorithm.KYBER768, OQSAlgorithm.KYBER1024]:
            raise OQSError(f"Unsupported Kyber algorithm: {algorithm}")

        # Ciphertext and shared secret sizes
        crypto_sizes = {
            OQSAlgorithm.KYBER512: (768, 32),
            OQSAlgorithm.KYBER768: (1088, 32),
            OQSAlgorithm.KYBER1024: (1568, 32)
        }

        ciphertext_size, shared_secret_size = crypto_sizes[algorithm]

        ciphertext = (ctypes.c_uint8 * ciphertext_size)()
        shared_secret = (ctypes.c_uint8 * shared_secret_size)()
        pub_key_array = (ctypes.c_uint8 * len(public_key))(*public_key)

        # Call appropriate encaps function
        kyber_names = {
            OQSAlgorithm.KYBER512: "512",
            OQSAlgorithm.KYBER768: "768",
            OQSAlgorithm.KYBER1024: "1024"
        }
        func_name = f"OQS_KEM_kyber_{kyber_names[algorithm]}_encaps"
        func = getattr(self.lib, func_name)
        result = func(ciphertext, shared_secret, pub_key_array)

        if result != 0:
            raise OQSError(f"Kyber encapsulation failed: {result}")

        return bytes(ciphertext), bytes(shared_secret)

    def kyber_decapsulate(self, algorithm: OQSAlgorithm, ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        Kyber decapsulation

        Args:
            algorithm: Kyber variant
            ciphertext: Received ciphertext
            secret_key: Recipient's secret key

        Returns:
            Shared secret
        """
        if algorithm not in [OQSAlgorithm.KYBER512, OQSAlgorithm.KYBER768, OQSAlgorithm.KYBER1024]:
            raise OQSError(f"Unsupported Kyber algorithm: {algorithm}")

        shared_secret_size = 32
        shared_secret = (ctypes.c_uint8 * shared_secret_size)()
        ciphertext_array = (ctypes.c_uint8 * len(ciphertext))(*ciphertext)
        secret_key_array = (ctypes.c_uint8 * len(secret_key))(*secret_key)

        # Call appropriate decaps function
        kyber_names = {
            OQSAlgorithm.KYBER512: "512",
            OQSAlgorithm.KYBER768: "768",
            OQSAlgorithm.KYBER1024: "1024"
        }
        func_name = f"OQS_KEM_kyber_{kyber_names[algorithm]}_decaps"
        func = getattr(self.lib, func_name)
        result = func(shared_secret, ciphertext_array, secret_key_array)

        if result != 0:
            raise OQSError(f"Kyber decapsulation failed: {result}")

        return bytes(shared_secret)

    # ============================================================================
    # Dilithium Signature Methods
    # ============================================================================

    def dilithium_keypair(self, algorithm: OQSAlgorithm) -> Tuple[bytes, bytes]:
        """
        Generate Dilithium keypair

        Args:
            algorithm: Dilithium variant (DILITHIUM2, DILITHIUM3, DILITHIUM5)

        Returns:
            Tuple of (public_key, secret_key)
        """
        if algorithm not in [OQSAlgorithm.DILITHIUM2, OQSAlgorithm.DILITHIUM3, OQSAlgorithm.DILITHIUM5]:
            raise OQSError(f"Unsupported Dilithium algorithm: {algorithm}")

        # Key sizes for different Dilithium variants
        key_sizes = {
            OQSAlgorithm.DILITHIUM2: (1312, 2528),
            OQSAlgorithm.DILITHIUM3: (1952, 4000),
            OQSAlgorithm.DILITHIUM5: (2592, 4864)
        }

        public_key_size, secret_key_size = key_sizes[algorithm]

        public_key = (ctypes.c_uint8 * public_key_size)()
        secret_key = (ctypes.c_uint8 * secret_key_size)()

        # Call appropriate keypair function
        variant = algorithm.value - 2  # DILITHIUM2=3, so 3-2=1, but we want 2
        variant_map = {OQSAlgorithm.DILITHIUM2: 2, OQSAlgorithm.DILITHIUM3: 3, OQSAlgorithm.DILITHIUM5: 5}
        variant_num = variant_map[algorithm]

        func_name = f"OQS_SIG_dilithium_{variant_num}_keypair"
        func = getattr(self.lib, func_name)
        result = func(public_key, secret_key)

        if result != 0:
            raise OQSError(f"Dilithium keypair generation failed: {result}")

        return bytes(public_key), bytes(secret_key)

    def dilithium_sign(self, algorithm: OQSAlgorithm, message: bytes, secret_key: bytes) -> bytes:
        """
        Dilithium signature generation

        Args:
            algorithm: Dilithium variant
            message: Message to sign
            secret_key: Signer's secret key

        Returns:
            Signature
        """
        if algorithm not in [OQSAlgorithm.DILITHIUM2, OQSAlgorithm.DILITHIUM3, OQSAlgorithm.DILITHIUM5]:
            raise OQSError(f"Unsupported Dilithium algorithm: {algorithm}")

        # Signature sizes for different Dilithium variants
        sig_sizes = {
            OQSAlgorithm.DILITHIUM2: 2420,
            OQSAlgorithm.DILITHIUM3: 3293,
            OQSAlgorithm.DILITHIUM5: 4595
        }

        signature_size = sig_sizes[algorithm]
        signature = (ctypes.c_uint8 * signature_size)()
        sig_len = ctypes.c_size_t(signature_size)
        message_array = (ctypes.c_uint8 * len(message))(*message)
        secret_key_array = (ctypes.c_uint8 * len(secret_key))(*secret_key)

        # Call appropriate sign function
        variant_map = {OQSAlgorithm.DILITHIUM2: 2, OQSAlgorithm.DILITHIUM3: 3, OQSAlgorithm.DILITHIUM5: 5}
        variant_num = variant_map[algorithm]

        func_name = f"OQS_SIG_dilithium_{variant_num}_sign"
        func = getattr(self.lib, func_name)
        result = func(signature, ctypes.byref(sig_len), message_array, len(message), secret_key_array)

        if result != 0:
            raise OQSError(f"Dilithium signing failed: {result}")

        return bytes(signature)[:sig_len.value]

    def dilithium_verify(self, algorithm: OQSAlgorithm, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Dilithium signature verification

        Args:
            algorithm: Dilithium variant
            message: Original message
            signature: Signature to verify
            public_key: Signer's public key

        Returns:
            True if signature is valid
        """
        if algorithm not in [OQSAlgorithm.DILITHIUM2, OQSAlgorithm.DILITHIUM3, OQSAlgorithm.DILITHIUM5]:
            raise OQSError(f"Unsupported Dilithium algorithm: {algorithm}")

        message_array = (ctypes.c_uint8 * len(message))(*message)
        signature_array = (ctypes.c_uint8 * len(signature))(*signature)
        public_key_array = (ctypes.c_uint8 * len(public_key))(*public_key)

        # Call appropriate verify function
        variant_map = {OQSAlgorithm.DILITHIUM2: 2, OQSAlgorithm.DILITHIUM3: 3, OQSAlgorithm.DILITHIUM5: 5}
        variant_num = variant_map[algorithm]

        func_name = f"OQS_SIG_dilithium_{variant_num}_verify"
        func = getattr(self.lib, func_name)
        result = func(message_array, len(message), signature_array, len(signature), public_key_array)

        return result == 0

    # ============================================================================
    # SHA3/SHAKE Methods (Using Python hashlib for compatibility)
    # ============================================================================

    def sha3_256(self, data: bytes) -> bytes:
        """Compute SHA3-256 hash using Python's hashlib"""
        import hashlib
        return hashlib.sha3_256(data).digest()

    def sha3_512(self, data: bytes) -> bytes:
        """Compute SHA3-512 hash using Python's hashlib"""
        import hashlib
        return hashlib.sha3_512(data).digest()

    def shake128(self, data: bytes, output_length: int) -> bytes:
        """Compute SHAKE128 XOF using Python's hashlib"""
        import hashlib
        return hashlib.shake_128(data).digest(output_length)

    def shake256(self, data: bytes, output_length: int) -> bytes:
        """Compute SHAKE256 XOF using Python's hashlib"""
        import hashlib
        return hashlib.shake_256(data).digest(output_length)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_oqs_bindings(lib_path: str = "/usr/local/lib/liboqs.so") -> OQSBindings:
    """
    Create and return OQS bindings instance

    Args:
        lib_path: Path to liboqs shared library

    Returns:
        Configured OQS bindings instance
    """
    return OQSBindings(lib_path)


def test_oqs_bindings(bindings: OQSBindings) -> bool:
    """
    Test OQS bindings functionality

    Args:
        bindings: OQS bindings instance

    Returns:
        True if all tests pass
    """
    try:
        # Test version
        version = bindings.get_version()
        print(f"liboqs version: {version}")

        # Test random bytes
        random_data = bindings.random_bytes(32)
        assert len(random_data) == 32
        print("✓ Random bytes generation works")

        # Test Kyber512
        pub_key, sec_key = bindings.kyber_keypair(OQSAlgorithm.KYBER512)
        assert len(pub_key) == 800
        assert len(sec_key) == 1632
        print("✓ Kyber512 keypair generation works")

        ciphertext, shared_secret_enc = bindings.kyber_encapsulate(OQSAlgorithm.KYBER512, pub_key)
        assert len(ciphertext) == 768
        assert len(shared_secret_enc) == 32
        print("✓ Kyber512 encapsulation works")

        shared_secret_dec = bindings.kyber_decapsulate(OQSAlgorithm.KYBER512, ciphertext, sec_key)
        assert shared_secret_enc == shared_secret_dec
        print("✓ Kyber512 decapsulation works")

        # Test Dilithium2
        pub_key_sig, sec_key_sig = bindings.dilithium_keypair(OQSAlgorithm.DILITHIUM2)
        assert len(pub_key_sig) == 1312
        assert len(sec_key_sig) == 2528
        print("✓ Dilithium2 keypair generation works")

        message = b"Hello, quantum world!"
        signature = bindings.dilithium_sign(OQSAlgorithm.DILITHIUM2, message, sec_key_sig)
        assert len(signature) == 2420
        print("✓ Dilithium2 signing works")

        is_valid = bindings.dilithium_verify(OQSAlgorithm.DILITHIUM2, message, signature, pub_key_sig)
        assert is_valid
        print("✓ Dilithium2 verification works")

        # Test SHA3
        test_data = b"test data for hashing"
        hash_256 = bindings.sha3_256(test_data)
        assert len(hash_256) == 32
        print("✓ SHA3-256 works")

        hash_512 = bindings.sha3_512(test_data)
        assert len(hash_512) == 64
        print("✓ SHA3-512 works")

        return True

    except Exception as e:
        print(f"✗ OQS bindings test failed: {e}")
        return False


# Global instance for convenience
_oqs_instance: Optional[OQSBindings] = None

def get_oqs_instance() -> OQSBindings:
    """Get global OQS bindings instance"""
    global _oqs_instance
    if _oqs_instance is None:
        _oqs_instance = create_oqs_bindings()
    return _oqs_instance


if __name__ == "__main__":
    # Test the bindings when run directly
    try:
        bindings = create_oqs_bindings()
        success = test_oqs_bindings(bindings)
        if success:
            print("\n🎉 All OQS bindings tests passed!")
        else:
            print("\n❌ Some OQS bindings tests failed!")
    except Exception as e:
        print(f"❌ Failed to create OQS bindings: {e}")