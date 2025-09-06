import ctypes
import os

# Load the shared library
_lib_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'libsudarshan.so')
_lib = ctypes.CDLL(_lib_path)

# Define the Buffer struct
class Buffer(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.POINTER(ctypes.c_uint8)),
        ('length', ctypes.c_size_t),
        ('capacity', ctypes.c_size_t),
        ('secure', ctypes.c_bool),
        ('locked', ctypes.c_bool),
    ]

# Define the EncryptionResult struct
class EncryptionResult(ctypes.Structure):
    _fields_ = [
        ('kem_ciphertext', Buffer),
        ('encrypted_payload', Buffer),
        ('payload_nonce', Buffer),
        ('payload_tag', Buffer),
        ('salt', Buffer),
        ('integrity_hash', Buffer),
        ('signature', Buffer),
        ('metadata', ctypes.c_char_p),
    ]

# Algorithm enums
SUDARSHAN_KEM_KYBER512 = 0
SUDARSHAN_KEM_KYBER768 = 1
SUDARSHAN_KEM_KYBER1024 = 2

SUDARSHAN_SIG_DILITHIUM2 = 0
SUDARSHAN_SIG_DILITHIUM3 = 1
SUDARSHAN_SIG_DILITHIUM5 = 2

SUDARSHAN_SYM_AES256GCM = 0
SUDARSHAN_SYM_CHACHA20POLY1305 = 1

# Error codes
SUDARSHAN_SUCCESS = 0
SUDARSHAN_ERROR_INVALID_ARGUMENT = -1
SUDARSHAN_ERROR_MEMORY_ALLOCATION = -2
SUDARSHAN_ERROR_BUFFER_TOO_SMALL = -3
SUDARSHAN_ERROR_NULL_POINTER = -4
SUDARSHAN_ERROR_INVALID_STATE = -5
SUDARSHAN_ERROR_CRYPTO_INIT_FAILED = -10
SUDARSHAN_ERROR_OQS_NOT_AVAILABLE = -11
SUDARSHAN_ERROR_ENCRYPTION_FAILED = -12
SUDARSHAN_ERROR_DECRYPTION_FAILED = -13
SUDARSHAN_ERROR_SIGNATURE_FAILED = -14
SUDARSHAN_ERROR_VERIFICATION_FAILED = -15
SUDARSHAN_ERROR_KEY_GENERATION_FAILED = -16
SUDARSHAN_ERROR_KEY_DERIVATION_FAILED = -17
SUDARSHAN_ERROR_UNSUPPORTED_ALGORITHM = -18
SUDARSHAN_ERROR_INVALID_KEY = -19
SUDARSHAN_ERROR_INVALID_SIGNATURE = -20
SUDARSHAN_ERROR_FILE_NOT_FOUND = -30
SUDARSHAN_ERROR_FILE_READ_FAILED = -31
SUDARSHAN_ERROR_FILE_WRITE_FAILED = -32
SUDARSHAN_ERROR_INVALID_FORMAT = -33
SUDARSHAN_ERROR_SECURITY_VIOLATION = -40
SUDARSHAN_ERROR_INTEGRITY_CHECK_FAILED = -41
SUDARSHAN_ERROR_AUTHENTICATION_FAILED = -42
SUDARSHAN_ERROR_AUTHORIZATION_FAILED = -43
SUDARSHAN_ERROR_NETWORK_UNAVAILABLE = -50
SUDARSHAN_ERROR_CONNECTION_FAILED = -51
SUDARSHAN_ERROR_TIMEOUT = -52
SUDARSHAN_ERROR_HARDWARE_NOT_AVAILABLE = -60
SUDARSHAN_ERROR_TPM_ERROR = -61
SUDARSHAN_ERROR_HSM_ERROR = -62
SUDARSHAN_ERROR_SECURE_ENCLAVE_ERROR = -63
SUDARSHAN_ERROR_INTERNAL_ERROR = -100
SUDARSHAN_ERROR_UNKNOWN = -999

# Function bindings

# sudarshan_crypto_init (mapped to sudarshan_crypto_engine_create)
_lib.sudarshan_crypto_init.argtypes = []
_lib.sudarshan_crypto_init.restype = ctypes.c_void_p

# sudarshan_crypto_cleanup
_lib.sudarshan_crypto_cleanup.argtypes = [ctypes.c_void_p]
_lib.sudarshan_crypto_cleanup.restype = None

# sudarshan_kem_keypair (mapped to sudarshan_crypto_generate_kem_keypair)
_lib.sudarshan_kem_keypair.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_kem_keypair.restype = ctypes.c_int

# sudarshan_encrypt_payload (mapped to sudarshan_crypto_encrypt)
_lib.sudarshan_encrypt_payload.argtypes = [ctypes.c_void_p, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.c_char_p, ctypes.POINTER(EncryptionResult)]
_lib.sudarshan_encrypt_payload.restype = ctypes.c_int

# sudarshan_decrypt_payload (mapped to sudarshan_crypto_decrypt)
_lib.sudarshan_decrypt_payload.argtypes = [ctypes.c_void_p, ctypes.POINTER(EncryptionResult), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_decrypt_payload.restype = ctypes.c_int

# Additional relevant functions

# sudarshan_kem_encapsulate
_lib.sudarshan_kem_encapsulate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_kem_encapsulate.restype = ctypes.c_int

# sudarshan_kem_decapsulate
_lib.sudarshan_kem_decapsulate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_kem_decapsulate.restype = ctypes.c_int

# sudarshan_sig_keypair
_lib.sudarshan_sig_keypair.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_sig_keypair.restype = ctypes.c_int

# sudarshan_sig_sign
_lib.sudarshan_sig_sign.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_sig_sign.restype = ctypes.c_int

# sudarshan_sig_verify
_lib.sudarshan_sig_verify.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_sig_verify.restype = ctypes.c_int

# sudarshan_sym_encrypt
_lib.sudarshan_sym_encrypt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_sym_encrypt.restype = ctypes.c_int

# sudarshan_sym_decrypt
_lib.sudarshan_sym_decrypt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_sym_decrypt.restype = ctypes.c_int

# sudarshan_hash_sha3_512
_lib.sudarshan_hash_sha3_512.argtypes = [ctypes.c_void_p, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
_lib.sudarshan_hash_sha3_512.restype = ctypes.c_int

# sudarshan_kdf_hkdf
_lib.sudarshan_kdf_hkdf.argtypes = [ctypes.c_void_p, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.POINTER(Buffer), ctypes.c_size_t, ctypes.POINTER(Buffer)]
_lib.sudarshan_kdf_hkdf.restype = ctypes.c_int

# sudarshan_random_bytes
_lib.sudarshan_random_bytes.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(Buffer)]
_lib.sudarshan_random_bytes.restype = ctypes.c_int

# sudarshan_crypto_get_error
_lib.sudarshan_crypto_get_error.argtypes = [ctypes.c_void_p]
_lib.sudarshan_crypto_get_error.restype = ctypes.c_char_p