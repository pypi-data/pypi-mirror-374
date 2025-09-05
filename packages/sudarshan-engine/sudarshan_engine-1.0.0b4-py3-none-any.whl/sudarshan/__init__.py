"""
Sudarshan Engine - Universal Quantum-Safe Cybersecurity Engine

A comprehensive security engine providing quantum-resistant encryption,
authentication, and protection for digital assets and applications.

Core Features:
- Post-Quantum Cryptography (NIST-approved algorithms)
- Box-in-a-Box layered securitey model
- .spq quantum-safe file format
- Universal applicability (wallets, databases, payments, etc.)
- Open-core freemium model

Version: 0.1.0
License: AGPLv3 (Free Tier), Commercial (Premium)
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime, timezone

# Import core components
from .spq_workflow import SPQWorkflow, SPQWorkflowError, get_spq_workflow
from .crypto import SudarshanCrypto, CryptoError, get_crypto_instance
from .protocols import BoxInBoxOrchestrator, ProtocolError
from .spq_format import Algorithm, Compression, SPQError

# Import from parent directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from bindings.oqs_bindings import OQSAlgorithm, get_oqs_instance
except ImportError:
    # Fallback for when bindings are not available
    OQSAlgorithm = None
    get_oqs_instance = None

__version__ = "0.1.0"
__author__ = "Sudarshan Engine Team"
__license__ = "AGPL-3.0"
__description__ = "Universal Quantum-Safe Cybersecurity Engine"

# Version info
VERSION_INFO = {
    "major": 0,
    "minor": 1,
    "patch": 0,
    "release": "alpha",
    "full": __version__
}

# Engine capabilities
ENGINE_FEATURES = {
    "quantum_safe": True,
    "pqc_algorithms": ["Kyber", "Dilithium", "Falcon"],
    "symmetric_crypto": ["AES-256-GCM", "ChaCha20-Poly1305"],
    "hash_functions": ["SHA3-512"],
    "file_format": ".spq",
    "box_in_box_layers": ["Inner Shield", "Outer Vault", "Isolation Room", "Transaction Capsule"],
    "platforms": ["Linux", "macOS", "Windows"],
    "freemium_model": True
}

# Freemium access control
FREE_TIER_LIMITS = {
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "max_operations_per_hour": 1000,
    "supported_algorithms": ["kyber1024", "dilithium5"],
    "compression_enabled": True,
    "api_access": False,
    "commercial_features": False
}

def get_engine_info() -> Dict[str, Any]:
    """Get comprehensive information about the Sudarshan Engine"""
    return {
        "name": "Sudarshan Engine",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "features": ENGINE_FEATURES,
        "version_info": VERSION_INFO,
        "free_tier_limits": FREE_TIER_LIMITS
    }

def is_quantum_safe() -> bool:
    """Check if the engine is quantum-safe"""
    return ENGINE_FEATURES["quantum_safe"]

def get_supported_algorithms() -> List[str]:
    """Get list of supported PQC algorithms"""
    return ENGINE_FEATURES["pqc_algorithms"]

def get_security_layers() -> List[str]:
    """Get the Box-in-a-Box security layers"""
    return ENGINE_FEATURES["box_in_box_layers"]

def check_free_tier_limits(data_size: int = 0, operation_count: int = 1) -> Dict[str, Any]:
    """Check if operation is within free tier limits"""
    result = {
        "within_limits": True,
        "warnings": [],
        "upgrade_required": False
    }

    if data_size > FREE_TIER_LIMITS["max_file_size"]:
        result["within_limits"] = False
        result["warnings"].append(f"File size {data_size} exceeds free tier limit of {FREE_TIER_LIMITS['max_file_size']}")
        result["upgrade_required"] = True

    if operation_count > FREE_TIER_LIMITS["max_operations_per_hour"]:
        result["within_limits"] = False
        result["warnings"].append(f"Operation count {operation_count} exceeds free tier limit of {FREE_TIER_LIMITS['max_operations_per_hour']}")
        result["upgrade_required"] = True

    return result

# ============================================================================
# Main API Functions
# ============================================================================

def spq_create(data: Union[bytes, str], recipient_public_key: bytes,
               output_path: Optional[str] = None,
               sender_secret_key: Optional[bytes] = None,
               metadata: Optional[Dict[str, Any]] = None,
               compression: str = "none",
               algorithm: str = "kyber1024") -> Dict[str, Any]:
    """
    Create a quantum-safe .spq file

    Args:
        data: Data to encrypt (bytes or string)
        recipient_public_key: Recipient's KEM public key
        output_path: Output file path (auto-generated if None)
        sender_secret_key: Sender's signature secret key (optional)
        metadata: Additional metadata dictionary
        compression: Compression type ("none", "zstd", "lz4", "brotli")
        algorithm: PQC algorithm ("kyber512", "kyber768", "kyber1024")

    Returns:
        Dict with creation results and file information

    Raises:
        SPQWorkflowError: If creation fails
        ValueError: If parameters are invalid
    """
    try:
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Check free tier limits
        limit_check = check_free_tier_limits(len(data))
        if not limit_check["within_limits"]:
            for warning in limit_check["warnings"]:
                print(f"Warning: {warning}")
            if limit_check["upgrade_required"]:
                raise ValueError("Operation exceeds free tier limits. Upgrade to premium for unlimited access.")

        # Validate algorithm
        if algorithm not in FREE_TIER_LIMITS["supported_algorithms"]:
            if algorithm not in ["kyber512", "kyber768", "dilithium2", "dilithium3", "falcon512", "falcon1024"]:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            print(f"Warning: {algorithm} requires premium tier")

        # Validate compression
        if compression not in ["none", "zstd", "lz4", "brotli"]:
            raise ValueError(f"Unsupported compression: {compression}")

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = f"encrypted_{timestamp}.spq"

        # Get workflow instance
        workflow = get_spq_workflow()

        # Parse algorithm and compression
        algo_enum = _parse_algorithm_string(algorithm)
        comp_enum = _parse_compression_string(compression)

        # Create .spq file
        result = workflow.create_spq_file(
            output_path, data, recipient_public_key,
            sender_secret_key, metadata, comp_enum, algo_enum
        )

        # Add additional metadata to result
        result.update({
            "engine_version": __version__,
            "created_with": "Sudarshan Engine Python SDK",
            "free_tier": True,
            "warnings": limit_check["warnings"]
        })

        return result

    except (SPQWorkflowError, CryptoError, ProtocolError) as e:
        raise SPQWorkflowError(f"Failed to create .spq file: {e}")
    except Exception as e:
        raise SPQWorkflowError(f"Unexpected error during .spq creation: {e}")

def spq_read(filepath: str, recipient_secret_key: bytes,
             sender_public_key: Optional[bytes] = None,
             output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Read and decrypt a .spq file

    Args:
        filepath: Path to .spq file
        recipient_secret_key: Recipient's KEM secret key
        sender_public_key: Sender's signature public key (optional)
        output_path: Output file path for decrypted data (optional)

    Returns:
        Dict with decryption results and metadata

    Raises:
        SPQWorkflowError: If reading/decryption fails
        ValueError: If parameters are invalid
    """
    try:
        # Validate input file
        if not os.path.exists(filepath):
            raise ValueError(f"Input file does not exist: {filepath}")

        # Check file size against free tier limits
        file_size = os.path.getsize(filepath)
        limit_check = check_free_tier_limits(file_size)
        if not limit_check["within_limits"]:
            for warning in limit_check["warnings"]:
                print(f"Warning: {warning}")
            if limit_check["upgrade_required"]:
                raise ValueError("File size exceeds free tier limits. Upgrade to premium for unlimited access.")

        # Get workflow instance
        workflow = get_spq_workflow()

        # Read and decrypt .spq file
        result = workflow.read_spq_file(
            filepath, recipient_secret_key, sender_public_key
        )

        # Write to output file if specified
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result['payload'])
            result['output_file'] = output_path

        # Add additional metadata to result
        result.update({
            "engine_version": __version__,
            "decrypted_with": "Sudarshan Engine Python SDK",
            "free_tier": True,
            "warnings": limit_check["warnings"]
        })

        return result

    except (SPQWorkflowError, CryptoError, ProtocolError) as e:
        raise SPQWorkflowError(f"Failed to read .spq file: {e}")
    except Exception as e:
        raise SPQWorkflowError(f"Unexpected error during .spq reading: {e}")

def spq_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a .spq file without decrypting

    Args:
        filepath: Path to .spq file

    Returns:
        Dict with file information and metadata, or None if invalid

    Raises:
        SPQWorkflowError: If file cannot be analyzed
    """
    try:
        if not os.path.exists(filepath):
            raise ValueError(f"File does not exist: {filepath}")

        workflow = get_spq_workflow()
        info = workflow.get_spq_info(filepath)

        if info:
            info.update({
                "engine_version": __version__,
                "analyzed_with": "Sudarshan Engine Python SDK",
                "free_tier": True
            })

        return info

    except Exception as e:
        raise SPQWorkflowError(f"Failed to analyze .spq file: {e}")

def generate_keypair(key_type: str = "kem", algorithm: str = "kyber1024") -> Dict[str, Any]:
    """
    Generate a PQC keypair

    Args:
        key_type: Type of keypair ("kem" or "signature")
        algorithm: PQC algorithm to use

    Returns:
        Dict with keypair and metadata

    Raises:
        ValueError: If parameters are invalid
        CryptoError: If key generation fails
    """
    try:
        crypto = get_crypto_instance()

        if key_type == "kem":
            public_key, secret_key = crypto.generate_kem_keypair(_parse_algorithm_string(algorithm))
        elif key_type == "signature":
            public_key, secret_key = crypto.generate_signature_keypair(_parse_algorithm_string(algorithm))
        else:
            raise ValueError(f"Invalid key type: {key_type}. Must be 'kem' or 'signature'")

        return {
            "key_type": key_type,
            "algorithm": algorithm,
            "public_key": public_key.hex(),
            "secret_key": secret_key.hex(),
            "public_key_bytes": public_key,
            "secret_key_bytes": secret_key,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": __version__,
            "free_tier": True
        }

    except Exception as e:
        raise CryptoError(f"Failed to generate keypair: {e}")

def validate_spq_file(filepath: str) -> Dict[str, Any]:
    """
    Validate .spq file integrity and security

    Args:
        filepath: Path to .spq file

    Returns:
        Dict with validation results

    Raises:
        SPQWorkflowError: If validation cannot be performed
    """
    try:
        if not os.path.exists(filepath):
            raise ValueError(f"File does not exist: {filepath}")

        workflow = get_spq_workflow()
        return workflow.validate_spq_security(filepath)

    except Exception as e:
        raise SPQWorkflowError(f"Failed to validate .spq file: {e}")

# ============================================================================
# Utility Functions
# ============================================================================

def _parse_algorithm_string(algorithm: str) -> OQSAlgorithm:
    """Parse algorithm string to OQSAlgorithm enum"""
    mapping = {
        "kyber512": OQSAlgorithm.KYBER512,
        "kyber768": OQSAlgorithm.KYBER768,
        "kyber1024": OQSAlgorithm.KYBER1024,
        "dilithium2": OQSAlgorithm.DILITHIUM2,
        "dilithium3": OQSAlgorithm.DILITHIUM3,
        "dilithium5": OQSAlgorithm.DILITHIUM5,
        "falcon512": OQSAlgorithm.FALCON512,
        "falcon1024": OQSAlgorithm.FALCON1024
    }

    if algorithm not in mapping:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Supported: {list(mapping.keys())}")

    return mapping[algorithm]

def _parse_compression_string(compression: str) -> Compression:
    """Parse compression string to Compression enum"""
    mapping = {
        "none": Compression.NONE,
        "zstd": Compression.ZSTD,
        "lz4": Compression.LZ4,
        "brotli": Compression.BROTLI
    }

    if compression not in mapping:
        raise ValueError(f"Unsupported compression: {compression}. Supported: {list(mapping.keys())}")

    return mapping[compression]

def save_keypair_to_file(keypair: Dict[str, Any], filepath: str) -> None:
    """
    Save a keypair to a JSON file

    Args:
        keypair: Keypair dict from generate_keypair()
        filepath: Output file path

    Raises:
        IOError: If file cannot be written
    """
    # Create a copy without binary keys for JSON serialization
    key_data = keypair.copy()
    key_data.pop('public_key_bytes', None)
    key_data.pop('secret_key_bytes', None)

    with open(filepath, 'w') as f:
        json.dump(key_data, f, indent=2)

    # Set restrictive permissions
    os.chmod(filepath, 0o600)

def load_keypair_from_file(filepath: str) -> Dict[str, Any]:
    """
    Load a keypair from a JSON file

    Args:
        filepath: Path to keypair file

    Returns:
        Dict with keypair data

    Raises:
        IOError: If file cannot be read
        ValueError: If file format is invalid
    """
    with open(filepath, 'r') as f:
        key_data = json.load(f)

    # Convert hex strings back to bytes
    if 'public_key' in key_data:
        key_data['public_key_bytes'] = bytes.fromhex(key_data['public_key'])
    if 'secret_key' in key_data:
        key_data['secret_key_bytes'] = bytes.fromhex(key_data['secret_key'])

    return key_data

# ============================================================================
# Convenience Classes
# ============================================================================

class SPQFileManager:
    """
    High-level manager for .spq file operations

    Provides a convenient interface for common .spq operations
    """

    def __init__(self):
        self.workflow = get_spq_workflow()

    def encrypt_file(self, input_path: str, output_path: str,
                    recipient_public_key: bytes, **kwargs) -> Dict[str, Any]:
        """Encrypt a file to .spq format"""
        with open(input_path, 'rb') as f:
            data = f.read()

        return spq_create(data, recipient_public_key, output_path, **kwargs)

    def decrypt_file(self, input_path: str, output_path: str,
                    recipient_secret_key: bytes, **kwargs) -> Dict[str, Any]:
        """Decrypt a .spq file"""
        result = spq_read(input_path, recipient_secret_key, **kwargs)

        with open(output_path, 'wb') as f:
            f.write(result['payload'])

        return result

    def encrypt_string(self, text: str, recipient_public_key: bytes, **kwargs) -> Dict[str, Any]:
        """Encrypt a string to .spq format"""
        return spq_create(text, recipient_public_key, **kwargs)

    def decrypt_string(self, filepath: str, recipient_secret_key: bytes, **kwargs) -> str:
        """Decrypt a .spq file to string"""
        result = spq_read(filepath, recipient_secret_key, **kwargs)
        return result['payload'].decode('utf-8')

# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    # Core functions
    "spq_create", "spq_read", "spq_info", "generate_keypair", "validate_spq_file",

    # Utility functions
    "save_keypair_to_file", "load_keypair_from_file",
    "check_free_tier_limits", "get_engine_info",
    "is_quantum_safe", "get_supported_algorithms", "get_security_layers",

    # Classes
    "SPQFileManager",

    # Exceptions
    "SPQWorkflowError", "CryptoError", "ProtocolError", "SPQError",

    # Constants
    "VERSION_INFO", "ENGINE_FEATURES", "FREE_TIER_LIMITS"
]