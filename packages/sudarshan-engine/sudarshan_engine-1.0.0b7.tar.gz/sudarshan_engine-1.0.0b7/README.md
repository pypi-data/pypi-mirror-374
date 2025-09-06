# Sudarshan Engine - Python Bindings

## What is Sudarshan Engine?

Sudarshan Engine is a high-performance, post-quantum secure cryptographic library written in C, designed to provide robust cryptographic primitives for modern applications. It implements state-of-the-art cryptographic algorithms including:

- **Post-Quantum Key Encapsulation Mechanisms (KEM)**: Kyber768 for quantum-resistant key exchange
- **Digital Signatures**: Dilithium for quantum-secure signatures
- **Symmetric Encryption**: AES-GCM for fast, secure data encryption
- **Hash Functions**: SHA3-512 for cryptographic hashing
- **Key Derivation**: HKDF for secure key derivation
- **Random Number Generation**: Cryptographically secure random bytes

The library is built with security, performance, and ease of use in mind, providing both low-level C APIs and high-level Python bindings.

## Python Bindings Overview

The Python bindings (`sudarshan-engine`) provide a user-friendly interface to the Sudarshan Engine C library, allowing Python developers to easily integrate post-quantum cryptography into their applications.

**Key Features:**
- Complete ctypes-based bindings to the C library
- Pythonic API with automatic error handling
- Support for all major cryptographic operations
- Cross-platform compatibility (Linux, macOS, Windows)
- No external dependencies beyond the C library

## Installation

```bash
pip install sudarshan-engine
```

**Requirements:**
- Python 3.6+
- The Sudarshan Engine shared library (`libsudarshan.so` on Linux, `libsudarshan.dylib` on macOS, `sudarshan.dll` on Windows)

## Quick Start

```python
from sudarshan.crypto import create_engine, generate_kem_keypair, encrypt, decrypt

# Initialize the crypto engine
engine = create_engine()

# Generate a keypair for key encapsulation
public_key, secret_key = generate_kem_keypair(engine)

# Encrypt data
ciphertext = encrypt(engine, public_key, b"Hello, World!")

# Decrypt data
plaintext = decrypt(engine, secret_key, ciphertext)

print(plaintext)  # b"Hello, World!"
```

## API Reference

### Core Functions

- `create_engine()`: Initialize a new crypto engine instance
- `cleanup_engine(engine)`: Clean up engine resources
- `generate_kem_keypair(engine)`: Generate Kyber768 keypair
- `kem_encapsulate(engine, public_key)`: Encapsulate shared secret
- `kem_decapsulate(engine, secret_key, ciphertext)`: Decapsulate shared secret
- `generate_sig_keypair(engine)`: Generate Dilithium signature keypair
- `sign(engine, secret_key, message)`: Sign a message
- `verify(engine, public_key, message, signature)`: Verify a signature
- `sym_encrypt(engine, key, plaintext)`: Symmetric encryption
- `sym_decrypt(engine, key, ciphertext)`: Symmetric decryption
- `hash_sha3_512(data)`: Compute SHA3-512 hash
- `kdf_hkdf(salt, ikm, info, length)`: Key derivation using HKDF
- `random_bytes(length)`: Generate cryptographically secure random bytes

## Project Structure

```
sudarshan_engine/
├── CMakeLists.txt              # Main C build system
├── src/                        # C core library source
│   ├── crypto.c
│   ├── crypto.h
│   └── ...
├── include/                    # Public C headers
├── bindings/
│   └── python/                 # Python bindings
│       ├── sudarshan/
│       │   ├── __init__.py
│       │   ├── crypto.py      # High-level Python API
│       │   └── _bindings.py   # Low-level ctypes bindings
│       ├── tests/
│       │   └── test_crypto.py
│       ├── setup.py
│       └── pyproject.toml
├── tests/                      # C library tests
├── docs/                       # Documentation
└── examples/                   # Usage examples
```

## Security Considerations

- All cryptographic operations are performed in the C library for maximum security
- Keys are handled securely with proper memory management
- The library uses post-quantum algorithms resistant to quantum attacks
- Regular security audits and updates are recommended

## GitHub Repository

The complete source code, documentation, and examples are available at:
**https://github.com/yourusername/sudarshan_engine**

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the examples in the `examples/` directory

## Roadmap

- Additional post-quantum algorithms
- Hardware acceleration support
- WebAssembly bindings
- Integration with popular Python frameworks
- Performance optimizations

The Sudarshan Engine Python bindings provide a powerful, secure, and easy-to-use interface for integrating post-quantum cryptography into Python applications.