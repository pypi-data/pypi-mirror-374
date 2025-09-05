# .spq File Format Specification

## Overview

The .spq file format is Sudarshan Engine's proprietary quantum-safe container for encrypted data. It provides end-to-end quantum-resistant encryption, integrity verification, and authenticated origin guarantees. The format is designed to be self-describing, tamper-evident, and quantum-safe against both current and future cryptographic attacks.

## File Structure

Every .spq file follows a fixed binary structure with the following sections:

```
┌─────────────────────────────────────────────────────────────┐
│                    .spq File Layout                          │
├─────────────────────────────────────────────────────────────┤
│  Magic Bytes (8 bytes)    │ "SUDARSHA"                      │
├─────────────────────────────────────────────────────────────┤
│  Header (16 bytes)        │ Version, Algo, Compression,    │
│                           │ Metadata Len, Payload Len       │
├─────────────────────────────────────────────────────────────┤
│  Metadata (variable)      │ JSON/CBOR human-readable info   │
├─────────────────────────────────────────────────────────────┤
│  Encrypted Payload (var)  │ Kyber KEM + AES/ChaCha20 data  │
├─────────────────────────────────────────────────────────────┤
│  Integrity Hash (64 bytes)│ SHA3-512 of encrypted payload   │
├─────────────────────────────────────────────────────────────┤
│  PQC Signature (variable) │ Dilithium/Falcon signature      │
└─────────────────────────────────────────────────────────────┘
```

## Section Details

### 1. Magic Bytes (8 bytes)

**Purpose**: File type identification and format validation.

**Value**: ASCII string "SUDARSHA"  
**Hex**: `53 55 44 41 52 53 48 41`

**Rationale**: Allows programs to instantly recognize .spq files and distinguish them from other formats.

### 2. Header (16 bytes)

**Purpose**: Essential metadata for parsing and processing the file.

**Structure**:
```
Offset  Length  Type    Description
0       2       uint16  Format version (current: 0x0001)
2       1       uint8   PQC Algorithm ID
3       1       uint8   Compression method
4       4       uint32  Metadata section length (bytes)
8       8       uint64  Encrypted payload length (bytes)
```

**Algorithm IDs**:
- `0x01`: Kyber512
- `0x02`: Kyber768
- `0x03`: Kyber1024 (recommended)
- `0x04`: Dilithium2
- `0x05`: Dilithium3
- `0x06`: Dilithium5 (recommended)
- `0x07`: Falcon-512
- `0x08`: Falcon-1024

**Compression Methods**:
- `0x00`: No compression
- `0x01`: Zstandard (Zstd)
- `0x02`: LZ4
- `0x03`: Brotli

### 3. Metadata Section (Variable Length)

**Purpose**: Human-readable and machine-readable information about the file contents.

**Format**: JSON (default) or CBOR (binary)

**Required Fields**:
```json
{
  "creator": "Sudarshan Engine",
  "created_at": "2025-09-02T08:20:15Z",
  "algorithm": "Kyber1024",
  "signature": "Dilithium5",
  "compression": "zstd",
  "original_size": 1024,
  "comment": "Encrypted document"
}
```

**Optional Fields**:
```json
{
  "expires_at": "2026-09-02T08:20:15Z",
  "recipient": "user@example.com",
  "tags": ["confidential", "finance"],
  "checksum": "sha256:abc123...",
  "permissions": ["read", "write"]
}
```

**CBOR vs JSON**:
- **CBOR**: More compact, faster parsing, better for constrained environments
- **JSON**: Human-readable, easier debugging, broader tool support

### 4. Encrypted Payload (Variable Length)

**Purpose**: The actual encrypted data with quantum-safe protection.

**Encryption Scheme**:
1. **Key Encapsulation**: Kyber KEM generates shared secret
2. **Symmetric Encryption**: AES-256-GCM or ChaCha20-Poly1305
3. **Key Derivation**: HKDF with quantum-resistant hash

**Process**:
```
Sender:
1. Generate Kyber keypair (public_key, secret_key)
2. Encapsulate shared_secret using recipient's public_key
3. Derive encryption_key from shared_secret using HKDF
4. Encrypt payload with encryption_key
5. Store public_key in metadata for recipient

Recipient:
1. Extract public_key from metadata
2. Decapsulate shared_secret using own secret_key
3. Derive encryption_key from shared_secret using HKDF
4. Decrypt payload with encryption_key
```

**Security Properties**:
- **Quantum-Resistant**: Kyber provides IND-CCA2 security against quantum attacks
- **Forward Secrecy**: Each file uses unique ephemeral keys
- **Authenticated Encryption**: AES-GCM/ChaCha20-Poly1305 provides confidentiality + integrity

### 5. Integrity Hash (64 bytes)

**Purpose**: Tamper detection for the encrypted payload.

**Algorithm**: SHA3-512

**Process**:
1. Hash the entire encrypted payload section
2. Store hash before signature section
3. Verify hash before decryption

**Rationale**: SHA3-512 is quantum-resistant and provides 256-bit security level.

### 6. PQC Signature (Variable Length)

**Purpose**: Authenticate the origin and integrity of the entire file.

**Algorithms**:
- Dilithium (recommended for speed)
- Falcon (alternative for different security properties)

**Process**:
1. Sign the integrity hash with sender's private key
2. Store signature as final section
3. Verify signature before any processing

**Security Properties**:
- **Existential Unforgeability**: Only sender can create valid signatures
- **Quantum-Resistant**: Dilithium/Falcon are NIST-approved PQC signatures
- **Non-Repudiation**: Sender cannot deny creating the file

## Cryptographic Design Principles

### Quantum Safety
- All cryptographic primitives are NIST-approved PQC algorithms
- No legacy algorithms (RSA, ECC) are used anywhere in the format
- Security levels meet or exceed 128-bit classical equivalents

### Stateless Operations
- Each .spq file is self-contained
- No external state or key reuse
- Ephemeral keys generated per file

### Fail-Fast Validation
- Magic bytes validated first
- Header parsed and validated
- Hash verified before decryption
- Signature verified before payload access
- Any failure terminates processing immediately

### Hardware Compatibility
- Designed to work with HSM/TPM/SGX when available
- Software fallback for systems without hardware security
- Attestation support for hardware-backed operations

## Implementation Considerations

### File Size Overhead
- Magic bytes: 8 bytes
- Header: 16 bytes
- Metadata: 200-500 bytes (JSON)
- Hash: 64 bytes
- Signature: 2-4 KB (Dilithium)
- **Total overhead**: ~3-5 KB per file

### Performance Characteristics
- Encryption: ~10-50 MB/s (depends on payload size)
- Decryption: ~50-200 MB/s
- Signature generation: ~1-5 ms
- Signature verification: ~0.5-2 ms

### Platform Support
- **Endianness**: Little-endian (x86/ARM native)
- **Integer Sizes**: Standard C types (uint8, uint16, uint32, uint64)
- **String Encoding**: UTF-8 for metadata
- **Path Separators**: Platform-independent

## Versioning and Extensibility

### Format Versions
- **Version 1 (Current)**: Basic .spq format with Kyber/Dilithium
- **Future Versions**: Extended algorithms, compression options, metadata fields

### Backward Compatibility
- Newer versions can read older .spq files
- Older implementations reject newer versions
- Version negotiation through header field

### Extension Points
- Reserved algorithm IDs for future PQC schemes
- Extensible metadata with custom fields
- Compression algorithm expansion
- Hardware-specific optimizations

## Security Analysis

### Threat Model
- **Quantum Attacks**: Shor's/Grover's algorithms
- **Classical Attacks**: Man-in-the-middle, replay, side-channel
- **Implementation Attacks**: Fault injection, timing analysis
- **Protocol Attacks**: Key reuse, signature malleability

### Security Guarantees
- **Confidentiality**: IND-CCA2 secure via Kyber + AES-GCM
- **Integrity**: SHA3-512 collision resistance
- **Authentication**: EUF-CMA secure via Dilithium/Falcon
- **Forward Secrecy**: Ephemeral keys per file
- **Non-Repudiation**: Digital signatures

### Attack Mitigation
- **Quantum**: PQC algorithms throughout
- **Side-Channel**: Hardware isolation when available
- **Replay**: Unique nonces and timestamps
- **Tampering**: Hash + signature verification
- **Key Compromise**: Forward secrecy design

## Usage Examples

### Creating a .spq File
```python
from sudarshan import spq_create

metadata = {
    "creator": "MyApp",
    "created_at": "2025-09-02T08:20:15Z",
    "algorithm": "Kyber1024",
    "signature": "Dilithium5"
}

spq_create("secret.spq", metadata, b"confidential data", "password")
```

### Reading a .spq File
```python
from sudarshan import spq_read

data = spq_read("secret.spq", "password")
print(f"Metadata: {data['metadata']}")
print(f"Payload: {data['payload']}")
```

## Compliance and Standards

### NIST Standards
- FIPS 205 (Dilithium)
- FIPS 206 (Falcon)
- FIPS 203 (Kyber)

### Industry Standards
- RFC 8949 (CBOR)
- RFC 8259 (JSON)
- NIST SP 800-185 (SHA3)

### Regulatory Compliance
- GDPR: Data protection and privacy
- SOX: Financial data integrity
- HIPAA: Healthcare data security

## Future Enhancements

### Planned Features
- **Streaming Encryption**: Support for large files
- **Multi-Recipient**: Encrypt for multiple recipients
- **Key Rotation**: Automatic key updates
- **Hardware Binding**: TPM/HSM integration
- **Audit Trails**: Embedded operation logs

### Research Directions
- **Threshold Cryptography**: Distributed key management
- **Homomorphic Encryption**: Computation on encrypted data
- **Zero-Knowledge Proofs**: Privacy-preserving verification

This specification provides a complete, quantum-safe file format that balances security, performance, and usability for the Sudarshan Engine ecosystem.