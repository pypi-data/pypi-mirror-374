from ._bindings import *
import ctypes

def create_engine():
    """Create a new Sudarshan crypto engine."""
    engine = _lib.sudarshan_crypto_init()
    if not engine:
        raise RuntimeError("Failed to create crypto engine")
    return engine

def cleanup_engine(engine):
    """Clean up the crypto engine."""
    _lib.sudarshan_crypto_cleanup(engine)

def generate_kem_keypair(engine, kem_alg):
    """Generate a KEM keypair."""
    public_key = Buffer()
    secret_key = Buffer()
    ret = _lib.sudarshan_kem_keypair(engine, kem_alg, ctypes.byref(public_key), ctypes.byref(secret_key))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"KEM keypair generation failed: {ret}")
    return (
        ctypes.string_at(public_key.data, public_key.length),
        ctypes.string_at(secret_key.data, secret_key.length)
    )

def kem_encapsulate(engine, kem_alg, public_key):
    """Encapsulate a shared secret using KEM."""
    pub_key_buf = Buffer()
    pub_key_buf.data = (ctypes.c_uint8 * len(public_key))(*public_key)
    pub_key_buf.length = len(public_key)
    ciphertext = Buffer()
    shared_secret = Buffer()
    ret = _lib.sudarshan_kem_encapsulate(engine, kem_alg, ctypes.byref(pub_key_buf), ctypes.byref(ciphertext), ctypes.byref(shared_secret))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"KEM encapsulation failed: {ret}")
    return (
        ctypes.string_at(ciphertext.data, ciphertext.length),
        ctypes.string_at(shared_secret.data, shared_secret.length)
    )

def kem_decapsulate(engine, kem_alg, secret_key, ciphertext):
    """Decapsulate a shared secret using KEM."""
    sec_key_buf = Buffer()
    sec_key_buf.data = (ctypes.c_uint8 * len(secret_key))(*secret_key)
    sec_key_buf.length = len(secret_key)
    ct_buf = Buffer()
    ct_buf.data = (ctypes.c_uint8 * len(ciphertext))(*ciphertext)
    ct_buf.length = len(ciphertext)
    shared_secret = Buffer()
    ret = _lib.sudarshan_kem_decapsulate(engine, kem_alg, ctypes.byref(sec_key_buf), ctypes.byref(ct_buf), ctypes.byref(shared_secret))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"KEM decapsulation failed: {ret}")
    return ctypes.string_at(shared_secret.data, shared_secret.length)

def generate_sig_keypair(engine, sig_alg):
    """Generate a signature keypair."""
    public_key = Buffer()
    secret_key = Buffer()
    ret = _lib.sudarshan_sig_keypair(engine, sig_alg, ctypes.byref(public_key), ctypes.byref(secret_key))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Signature keypair generation failed: {ret}")
    return (
        ctypes.string_at(public_key.data, public_key.length),
        ctypes.string_at(secret_key.data, secret_key.length)
    )

def sign(engine, sig_alg, secret_key, message):
    """Sign a message."""
    sec_key_buf = Buffer()
    sec_key_buf.data = (ctypes.c_uint8 * len(secret_key))(*secret_key)
    sec_key_buf.length = len(secret_key)
    msg_buf = Buffer()
    msg_buf.data = (ctypes.c_uint8 * len(message))(*message)
    msg_buf.length = len(message)
    signature = Buffer()
    ret = _lib.sudarshan_sig_sign(engine, sig_alg, ctypes.byref(sec_key_buf), ctypes.byref(msg_buf), ctypes.byref(signature))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Signing failed: {ret}")
    return ctypes.string_at(signature.data, signature.length)

def verify(engine, sig_alg, public_key, message, signature):
    """Verify a signature."""
    pub_key_buf = Buffer()
    pub_key_buf.data = (ctypes.c_uint8 * len(public_key))(*public_key)
    pub_key_buf.length = len(public_key)
    msg_buf = Buffer()
    msg_buf.data = (ctypes.c_uint8 * len(message))(*message)
    msg_buf.length = len(message)
    sig_buf = Buffer()
    sig_buf.data = (ctypes.c_uint8 * len(signature))(*signature)
    sig_buf.length = len(signature)
    ret = _lib.sudarshan_sig_verify(engine, sig_alg, ctypes.byref(pub_key_buf), ctypes.byref(msg_buf), ctypes.byref(sig_buf))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Verification failed: {ret}")
    return True

def sym_encrypt(engine, sym_alg, key, nonce, aad, plaintext):
    """Symmetric encryption."""
    key_buf = Buffer()
    key_buf.data = (ctypes.c_uint8 * len(key))(*key)
    key_buf.length = len(key)
    nonce_buf = Buffer()
    nonce_buf.data = (ctypes.c_uint8 * len(nonce))(*nonce)
    nonce_buf.length = len(nonce)
    aad_buf = Buffer()
    aad_buf.data = (ctypes.c_uint8 * len(aad))(*aad)
    aad_buf.length = len(aad)
    pt_buf = Buffer()
    pt_buf.data = (ctypes.c_uint8 * len(plaintext))(*plaintext)
    pt_buf.length = len(plaintext)
    ciphertext = Buffer()
    tag = Buffer()
    ret = _lib.sudarshan_sym_encrypt(engine, sym_alg, ctypes.byref(key_buf), ctypes.byref(nonce_buf), ctypes.byref(aad_buf), ctypes.byref(pt_buf), ctypes.byref(ciphertext), ctypes.byref(tag))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Symmetric encryption failed: {ret}")
    return (
        ctypes.string_at(ciphertext.data, ciphertext.length),
        ctypes.string_at(tag.data, tag.length)
    )

def sym_decrypt(engine, sym_alg, key, nonce, aad, ciphertext, tag):
    """Symmetric decryption."""
    key_buf = Buffer()
    key_buf.data = (ctypes.c_uint8 * len(key))(*key)
    key_buf.length = len(key)
    nonce_buf = Buffer()
    nonce_buf.data = (ctypes.c_uint8 * len(nonce))(*nonce)
    nonce_buf.length = len(nonce)
    aad_buf = Buffer()
    aad_buf.data = (ctypes.c_uint8 * len(aad))(*aad)
    aad_buf.length = len(aad)
    ct_buf = Buffer()
    ct_buf.data = (ctypes.c_uint8 * len(ciphertext))(*ciphertext)
    ct_buf.length = len(ciphertext)
    tag_buf = Buffer()
    tag_buf.data = (ctypes.c_uint8 * len(tag))(*tag)
    tag_buf.length = len(tag)
    plaintext = Buffer()
    ret = _lib.sudarshan_sym_decrypt(engine, sym_alg, ctypes.byref(key_buf), ctypes.byref(nonce_buf), ctypes.byref(aad_buf), ctypes.byref(ct_buf), ctypes.byref(tag_buf), ctypes.byref(plaintext))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Symmetric decryption failed: {ret}")
    return ctypes.string_at(plaintext.data, plaintext.length)

def hash_sha3_512(engine, data):
    """Compute SHA3-512 hash."""
    data_buf = Buffer()
    data_buf.data = (ctypes.c_uint8 * len(data))(*data)
    data_buf.length = len(data)
    hash_out = Buffer()
    ret = _lib.sudarshan_hash_sha3_512(engine, ctypes.byref(data_buf), ctypes.byref(hash_out))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Hashing failed: {ret}")
    return ctypes.string_at(hash_out.data, hash_out.length)

def kdf_hkdf(engine, salt, ikm, info, length):
    """Derive key using HKDF."""
    salt_buf = Buffer()
    salt_buf.data = (ctypes.c_uint8 * len(salt))(*salt)
    salt_buf.length = len(salt)
    ikm_buf = Buffer()
    ikm_buf.data = (ctypes.c_uint8 * len(ikm))(*ikm)
    ikm_buf.length = len(ikm)
    info_buf = Buffer()
    info_buf.data = (ctypes.c_uint8 * len(info))(*info)
    info_buf.length = len(info)
    okm = Buffer()
    ret = _lib.sudarshan_kdf_hkdf(engine, ctypes.byref(salt_buf), ctypes.byref(ikm_buf), ctypes.byref(info_buf), length, ctypes.byref(okm))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Key derivation failed: {ret}")
    return ctypes.string_at(okm.data, okm.length)

def random_bytes(engine, length):
    """Generate random bytes."""
    random_buf = Buffer()
    ret = _lib.sudarshan_random_bytes(engine, length, ctypes.byref(random_buf))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Random bytes generation failed: {ret}")
    return ctypes.string_at(random_buf.data, random_buf.length)

def encrypt(engine, public_key, payload, metadata=None):
    """Encrypt payload using public key."""
    pub_key_buf = Buffer()
    pub_key_buf.data = (ctypes.c_uint8 * len(public_key))(*public_key)
    pub_key_buf.length = len(public_key)
    payload_buf = Buffer()
    payload_buf.data = (ctypes.c_uint8 * len(payload))(*payload)
    payload_buf.length = len(payload)
    result = EncryptionResult()
    ret = _lib.sudarshan_encrypt_payload(engine, ctypes.byref(pub_key_buf), ctypes.byref(payload_buf), None, metadata, ctypes.byref(result))
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Encryption failed: {ret}")
    return {
        'kem_ciphertext': ctypes.string_at(result.kem_ciphertext.data, result.kem_ciphertext.length),
        'encrypted_payload': ctypes.string_at(result.encrypted_payload.data, result.encrypted_payload.length),
        'payload_nonce': ctypes.string_at(result.payload_nonce.data, result.payload_nonce.length),
        'payload_tag': ctypes.string_at(result.payload_tag.data, result.payload_tag.length),
        'salt': ctypes.string_at(result.salt.data, result.salt.length),
        'integrity_hash': ctypes.string_at(result.integrity_hash.data, result.integrity_hash.length),
        'signature': ctypes.string_at(result.signature.data, result.signature.length),
        'metadata': result.metadata.decode() if result.metadata else None
    }

def decrypt(engine, kem_ciphertext, encrypted_payload, payload_nonce, payload_tag, salt, integrity_hash, signature, secret_key):
    """Decrypt payload using secret key."""
    kem_ct_buf = Buffer()
    kem_ct_buf.data = (ctypes.c_uint8 * len(kem_ciphertext))(*kem_ciphertext)
    kem_ct_buf.length = len(kem_ciphertext)
    enc_payload_buf = Buffer()
    enc_payload_buf.data = (ctypes.c_uint8 * len(encrypted_payload))(*encrypted_payload)
    enc_payload_buf.length = len(encrypted_payload)
    nonce_buf = Buffer()
    nonce_buf.data = (ctypes.c_uint8 * len(payload_nonce))(*payload_nonce)
    nonce_buf.length = len(payload_nonce)
    tag_buf = Buffer()
    tag_buf.data = (ctypes.c_uint8 * len(payload_tag))(*payload_tag)
    tag_buf.length = len(payload_tag)
    salt_buf = Buffer()
    salt_buf.data = (ctypes.c_uint8 * len(salt))(*salt)
    salt_buf.length = len(salt)
    hash_buf = Buffer()
    hash_buf.data = (ctypes.c_uint8 * len(integrity_hash))(*integrity_hash)
    hash_buf.length = len(integrity_hash)
    sig_buf = Buffer()
    sig_buf.data = (ctypes.c_uint8 * len(signature))(*signature)
    sig_buf.length = len(signature)
    sec_key_buf = Buffer()
    sec_key_buf.data = (ctypes.c_uint8 * len(secret_key))(*secret_key)
    sec_key_buf.length = len(secret_key)
    result = EncryptionResult()
    result.kem_ciphertext = kem_ct_buf
    result.encrypted_payload = enc_payload_buf
    result.payload_nonce = nonce_buf
    result.payload_tag = tag_buf
    result.salt = salt_buf
    result.integrity_hash = hash_buf
    result.signature = sig_buf
    decrypted_payload = Buffer()
    ret = _lib.sudarshan_decrypt_payload(engine, ctypes.byref(result), ctypes.byref(sec_key_buf), ctypes.byref(decrypted_payload), None)
    if ret != SUDARSHAN_SUCCESS:
        raise RuntimeError(f"Decryption failed: {ret}")
    return ctypes.string_at(decrypted_payload.data, decrypted_payload.length)

def get_error(engine):
    """Get the last error message."""
    return _lib.sudarshan_crypto_get_error(engine).decode()