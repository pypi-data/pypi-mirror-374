"""
Sudarshan Engine .spq File Format Handler

This module provides serialization and deserialization functionality for .spq files,
which are quantum-safe encrypted containers using post-quantum cryptography.

.spq File Structure:
- Magic Bytes (8): "SUDARSHA"
- Header (16): version, algo, compression, metadata_len, payload_len
- Metadata (var): JSON/CBOR human-readable info
- Encrypted Payload (var): Kyber KEM + AES/ChaCha20 encrypted data
- Integrity Hash (64): SHA3-512 of encrypted payload
- PQC Signature (var): Dilithium/Falcon signature
"""

import struct
import json
import hashlib
import os
from typing import Dict, Any, Tuple, Optional, BinaryIO
from enum import IntEnum


class Algorithm(IntEnum):
    """PQC Algorithm Identifiers"""
    KYBER512 = 0x01
    KYBER768 = 0x02
    KYBER1024 = 0x03  # Recommended
    DILITHIUM2 = 0x04
    DILITHIUM3 = 0x05
    DILITHIUM5 = 0x06  # Recommended
    FALCON512 = 0x07
    FALCON1024 = 0x08


class Compression(IntEnum):
    """Compression Method Identifiers"""
    NONE = 0x00
    ZSTD = 0x01
    LZ4 = 0x02
    BROTLI = 0x03
    ZLIB = 0x04  # Fallback compression when LZ4/Brotli not available


class SPQError(Exception):
    """Base exception for .spq format errors"""
    pass


class SPQValidationError(SPQError):
    """Raised when .spq file validation fails"""
    pass


class SPQFormatError(SPQError):
    """Raised when .spq file format is invalid"""
    pass


class SPQHeader:
    """Represents the .spq file header"""

    FORMAT = '<HHLLQ'  # Little-endian: 2 uint16, 1 uint8, 1 uint8, 4 uint32, 8 uint64
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, version: int = 0x0001, algorithm: Algorithm = Algorithm.KYBER1024,
                 compression: Compression = Compression.NONE, metadata_len: int = 0,
                 payload_len: int = 0):
        self.version = version
        self.algorithm = algorithm
        self.compression = compression
        self.metadata_len = metadata_len
        self.payload_len = payload_len

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SPQHeader':
        """Parse header from bytes"""
        if len(data) != cls.SIZE:
            raise SPQFormatError(f"Invalid header size: {len(data)}, expected {cls.SIZE}")

        try:
            version, algo_id, comp_id, metadata_len, payload_len = struct.unpack(cls.FORMAT, data)
            algorithm = Algorithm(algo_id)
            compression = Compression(comp_id)
            return cls(version, algorithm, compression, metadata_len, payload_len)
        except (struct.error, ValueError) as e:
            raise SPQFormatError(f"Failed to parse header: {e}")

    def to_bytes(self) -> bytes:
        """Serialize header to bytes"""
        return struct.pack(self.FORMAT, self.version, self.algorithm.value,
                          self.compression.value, self.metadata_len, self.payload_len)

    def __repr__(self) -> str:
        return (f"SPQHeader(version=0x{self.version:04X}, algorithm={self.algorithm.name}, "
                f"compression={self.compression.name}, metadata_len={self.metadata_len}, "
                f"payload_len={self.payload_len})")


class SPQMetadata:
    """Handles .spq metadata serialization/deserialization"""

    REQUIRED_FIELDS = ['creator', 'created_at', 'algorithm', 'signature']

    @staticmethod
    def validate(metadata: Dict[str, Any]) -> None:
        """Validate metadata structure"""
        for field in SPQMetadata.REQUIRED_FIELDS:
            if field not in metadata:
                raise SPQValidationError(f"Missing required metadata field: {field}")

        # Validate algorithm field
        if metadata['algorithm'] not in [algo.name for algo in Algorithm]:
            raise SPQValidationError(f"Invalid algorithm: {metadata['algorithm']}")

    @staticmethod
    def to_json(metadata: Dict[str, Any]) -> bytes:
        """Serialize metadata to JSON bytes"""
        SPQMetadata.validate(metadata)
        return json.dumps(metadata, separators=(',', ':')).encode('utf-8')

    @staticmethod
    def from_json(data: bytes) -> Dict[str, Any]:
        """Deserialize metadata from JSON bytes"""
        try:
            metadata = json.loads(data.decode('utf-8'))
            SPQMetadata.validate(metadata)
            return metadata
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise SPQFormatError(f"Failed to parse metadata JSON: {e}")


class SPQFile:
    """Main .spq file handler"""

    MAGIC_BYTES = b'SUDARSHA'
    MAGIC_SIZE = len(MAGIC_BYTES)
    HASH_SIZE = 64  # SHA3-512

    def __init__(self, header: SPQHeader, metadata: Dict[str, Any],
                 encrypted_payload: bytes, integrity_hash: bytes, signature: bytes):
        self.header = header
        self.metadata = metadata
        self.encrypted_payload = encrypted_payload
        self.integrity_hash = integrity_hash
        self.signature = signature

    @classmethod
    def create(cls, metadata: Dict[str, Any], encrypted_payload: bytes,
               integrity_hash: bytes, signature: bytes,
               algorithm: Algorithm = Algorithm.KYBER1024,
               compression: Compression = Compression.NONE) -> 'SPQFile':
        """Create a new .spq file structure"""
        # Serialize metadata
        metadata_bytes = SPQMetadata.to_json(metadata)
        metadata_len = len(metadata_bytes)
        payload_len = len(encrypted_payload)

        # Create header
        header = SPQHeader(algorithm=algorithm, compression=compression,
                          metadata_len=metadata_len, payload_len=payload_len)

        return cls(header, metadata, encrypted_payload, integrity_hash, signature)

    @classmethod
    def read(cls, filepath: str) -> 'SPQFile':
        """Read and parse .spq file from disk"""
        with open(filepath, 'rb') as f:
            return cls._read_from_stream(f)

    @classmethod
    def _read_from_stream(cls, stream: BinaryIO) -> 'SPQFile':
        """Read .spq file from binary stream"""
        # Read and validate magic bytes
        magic = stream.read(cls.MAGIC_SIZE)
        if magic != cls.MAGIC_BYTES:
            raise SPQValidationError(f"Invalid magic bytes: {magic.hex()}, expected {cls.MAGIC_BYTES.hex()}")

        # Read header
        header_data = stream.read(SPQHeader.SIZE)
        header = SPQHeader.from_bytes(header_data)

        # Read metadata
        metadata_data = stream.read(header.metadata_len)
        if len(metadata_data) != header.metadata_len:
            raise SPQFormatError(f"Incomplete metadata: got {len(metadata_data)}, expected {header.metadata_len}")
        metadata = SPQMetadata.from_json(metadata_data)

        # Read encrypted payload
        encrypted_payload = stream.read(header.payload_len)
        if len(encrypted_payload) != header.payload_len:
            raise SPQFormatError(f"Incomplete payload: got {len(encrypted_payload)}, expected {header.payload_len}")

        # Read integrity hash
        integrity_hash = stream.read(cls.HASH_SIZE)
        if len(integrity_hash) != cls.HASH_SIZE:
            raise SPQFormatError(f"Incomplete hash: got {len(integrity_hash)}, expected {cls.HASH_SIZE}")

        # Read signature (remaining data)
        signature = stream.read()

        return cls(header, metadata, encrypted_payload, integrity_hash, signature)

    def write(self, filepath: str) -> None:
        """Write .spq file to disk"""
        with open(filepath, 'wb') as f:
            self._write_to_stream(f)

        # Set restrictive permissions
        os.chmod(filepath, 0o600)  # Owner read/write only

    def _write_to_stream(self, stream: BinaryIO) -> None:
        """Write .spq file to binary stream"""
        # Write magic bytes
        stream.write(self.MAGIC_BYTES)

        # Write header
        stream.write(self.header.to_bytes())

        # Write metadata
        metadata_bytes = SPQMetadata.to_json(self.metadata)
        stream.write(metadata_bytes)

        # Write encrypted payload
        stream.write(self.encrypted_payload)

        # Write integrity hash
        stream.write(self.integrity_hash)

        # Write signature
        stream.write(self.signature)

    def verify_integrity(self) -> bool:
        """Verify the integrity hash of the encrypted payload"""
        computed_hash = hashlib.sha3_512(self.encrypted_payload).digest()
        return computed_hash == self.integrity_hash

    def get_total_size(self) -> int:
        """Calculate total file size"""
        metadata_bytes = SPQMetadata.to_json(self.metadata)
        return (self.MAGIC_SIZE + SPQHeader.SIZE + len(metadata_bytes) +
                len(self.encrypted_payload) + self.HASH_SIZE + len(self.signature))

    def __repr__(self) -> str:
        return (f"SPQFile(header={self.header}, metadata_keys={list(self.metadata.keys())}, "
                f"payload_size={len(self.encrypted_payload)}, signature_size={len(self.signature)})")


# Utility functions

def compute_integrity_hash(data: bytes) -> bytes:
    """Compute SHA3-512 integrity hash"""
    return hashlib.sha3_512(data).digest()


def validate_spq_file(filepath: str) -> Tuple[bool, Optional[str]]:
    """
    Validate .spq file structure and integrity

    Returns:
        (is_valid, error_message)
    """
    try:
        spq_file = SPQFile.read(filepath)

        # Verify magic bytes (already done in read)
        # Verify header (already done in read)
        # Verify metadata (already done in read)

        # Verify payload integrity
        if not spq_file.verify_integrity():
            return False, "Integrity hash mismatch"

        # Additional validations can be added here
        # (signature verification would require crypto keys)

        return True, None

    except (SPQError, OSError) as e:
        return False, str(e)


def get_spq_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Get information about .spq file without decrypting

    Returns metadata and file statistics
    """
    try:
        spq_file = SPQFile.read(filepath)
        return {
            'metadata': spq_file.metadata,
            'algorithm': spq_file.header.algorithm.name,
            'compression': spq_file.header.compression.name,
            'payload_size': len(spq_file.encrypted_payload),
            'total_size': spq_file.get_total_size(),
            'integrity_verified': spq_file.verify_integrity()
        }
    except SPQError:
        return None