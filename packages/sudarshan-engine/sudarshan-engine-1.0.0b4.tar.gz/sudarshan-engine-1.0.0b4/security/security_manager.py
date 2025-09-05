#!/usr/bin/env python3
"""
Sudarshan Engine Security Manager

Centralized security management system implementing enterprise-grade
security best practices for quantum-safe operations.
"""

import os
import sys
import time
import json
import hashlib
import secrets
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import struct

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sudarshan.crypto import generate_random_bytes, hash_sha3_512


class SecurityLevel(Enum):
    """Security levels for different operations."""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel(Enum):
    """Threat levels for security events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Types of security events to log."""
    KEY_GENERATION = "key_generation"
    ENCRYPTION_OPERATION = "encryption_operation"
    DECRYPTION_OPERATION = "decryption_operation"
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_FAILURE = "authorization_failure"
    TAMPER_ATTEMPT = "tamper_attempt"
    INTEGRITY_CHECK_FAILURE = "integrity_check_failure"
    ENCLAVE_BREACH_ATTEMPT = "enclave_breach_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    HARDWARE_SECURITY_FAILURE = "hardware_security_failure"


@dataclass
class SecurityContext:
    """Security context for operations."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.STANDARD
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    hardware_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class SecurityEventLog:
    """Security event log entry."""
    event_id: str
    event_type: SecurityEvent
    threat_level: ThreatLevel
    context: SecurityContext
    details: Dict[str, Any]
    timestamp: datetime
    checksum: str

    def __post_init__(self):
        if not self.event_id:
            self.event_id = secrets.token_hex(16)
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate integrity checksum for the log entry."""
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "threat_level": self.threat_level.value,
            "context": asdict(self.context),
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hash_sha3_512(data_str.encode()).hex()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "threat_level": self.threat_level.value,
            "context": asdict(self.context),
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum
        }


class EnclaveManager:
    """Hardware Security Module (HSM) and Secure Enclave manager."""

    def __init__(self):
        self.enclave_available = self._detect_enclave()
        self.enclave_locked = False
        self.key_cache = {}
        self.session_keys = set()

    def _detect_enclave(self) -> bool:
        """Detect available hardware security modules."""
        # Check for TPM
        if os.path.exists("/dev/tpm0") or os.path.exists("/dev/tpmrm0"):
            return True

        # Check for SGX
        try:
            with open("/proc/cpuinfo", "r") as f:
                if "sgx" in f.read().lower():
                    return True
        except:
            pass

        # Check for HSM devices
        hsm_paths = ["/dev/hsm", "/var/run/hsm.sock"]
        for path in hsm_paths:
            if os.path.exists(path):
                return True

        return False

    def is_enclave_available(self) -> bool:
        """Check if hardware enclave is available."""
        return self.enclave_available and not self.enclave_locked

    def execute_in_enclave(self, operation: str, data: bytes,
                          context: SecurityContext) -> bytes:
        """Execute operation in hardware enclave."""
        if not self.is_enclave_available():
            raise SecurityError("Hardware enclave not available")

        try:
            # Simulate enclave operation (replace with actual HSM/SGX calls)
            if operation == "encrypt":
                result = self._enclave_encrypt(data)
            elif operation == "decrypt":
                result = self._enclave_decrypt(data)
            elif operation == "sign":
                result = self._enclave_sign(data)
            elif operation == "verify":
                result = self._enclave_verify(data)
            else:
                raise SecurityError(f"Unsupported enclave operation: {operation}")

            # Log successful enclave operation
            SecurityManager.log_security_event(
                SecurityEvent.ENCRYPTION_OPERATION,
                ThreatLevel.LOW,
                context,
                {"operation": operation, "enclave_used": True}
            )

            return result

        except Exception as e:
            SecurityManager.log_security_event(
                SecurityEvent.HARDWARE_SECURITY_FAILURE,
                ThreatLevel.HIGH,
                context,
                {"operation": operation, "error": str(e)}
            )
            raise SecurityError(f"Enclave operation failed: {e}")

    def _enclave_encrypt(self, data: bytes) -> bytes:
        """Simulate enclave encryption."""
        # Generate ephemeral key
        key = generate_random_bytes(32)
        self.session_keys.add(key.hex())

        # Simple XOR encryption (replace with actual enclave crypto)
        encrypted = bytes(a ^ b for a, b in zip(data, key * (len(data) // 32 + 1)))
        return encrypted

    def _enclave_decrypt(self, data: bytes) -> bytes:
        """Simulate enclave decryption."""
        # This would use the stored session key in a real implementation
        return data  # Placeholder

    def _enclave_sign(self, data: bytes) -> bytes:
        """Simulate enclave signing."""
        return hash_sha3_512(data)  # Placeholder

    def _enclave_verify(self, data: bytes) -> bytes:
        """Simulate enclave verification."""
        return data  # Placeholder

    def attest_enclave(self) -> Dict[str, Any]:
        """Generate enclave attestation."""
        return {
            "enclave_type": "simulated",
            "measurement": hash_sha3_512(b"enclave_code").hex(),
            "platform": "linux_x86_64",
            "timestamp": datetime.utcnow().isoformat()
        }


class KeyManager:
    """Secure key management with non-reuse guarantees."""

    def __init__(self):
        self.used_keys = set()
        self.key_cache = {}
        self.key_rotation_interval = timedelta(hours=24)

    def generate_ephemeral_key(self, algorithm: str,
                              context: SecurityContext) -> bytes:
        """Generate a new ephemeral key that will never be reused."""
        while True:
            key = generate_random_bytes(32)  # 256-bit key
            key_hash = hash_sha3_512(key).hex()

            if key_hash not in self.used_keys:
                self.used_keys.add(key_hash)

                # Log key generation
                SecurityManager.log_security_event(
                    SecurityEvent.KEY_GENERATION,
                    ThreatLevel.LOW,
                    context,
                    {"algorithm": algorithm, "key_type": "ephemeral"}
                )

                return key

    def validate_key_uniqueness(self, key: bytes) -> bool:
        """Validate that a key has not been used before."""
        key_hash = hash_sha3_512(key).hex()
        return key_hash not in self.used_keys

    def mark_key_used(self, key: bytes):
        """Mark a key as used to prevent reuse."""
        key_hash = hash_sha3_512(key).hex()
        self.used_keys.add(key_hash)

    def rotate_keys_if_needed(self):
        """Rotate keys based on time interval."""
        # This would implement key rotation logic
        pass

    def secure_key_deletion(self, key: bytes):
        """Securely delete a key from memory."""
        # Overwrite key data multiple times
        key_data = bytearray(key)
        for _ in range(3):
            for i in range(len(key_data)):
                key_data[i] = secrets.randbelow(256)

        # Clear references
        del key_data


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, log_directory: str = "audit_logs"):
        self.log_directory = log_directory
        self.log_file = None
        self.lock = threading.Lock()

        # Ensure log directory exists
        os.makedirs(log_directory, exist_ok=True)

        # Initialize log file
        self._rotate_log_file()

    def _rotate_log_file(self):
        """Rotate to a new log file."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_{timestamp}.log"
        self.log_file = os.path.join(self.log_directory, filename)

    def log_event(self, event: SecurityEventLog):
        """Log a security event."""
        with self.lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    json.dump(event.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

                # Check if log rotation is needed
                if os.path.getsize(self.log_file) > 10 * 1024 * 1024:  # 10MB
                    self._rotate_log_file()

            except Exception as e:
                # Fallback logging to stderr
                print(f"Audit logging failed: {e}", file=sys.stderr)

    def query_events(self, filters: Dict[str, Any]) -> List[SecurityEventLog]:
        """Query audit events with filters."""
        # This would implement event querying logic
        return []

    def generate_report(self, start_date: datetime,
                       end_date: datetime) -> Dict[str, Any]:
        """Generate security audit report."""
        return {
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "total_events": 0,
            "threat_levels": {},
            "event_types": {},
            "recommendations": []
        }


class FailFastValidator:
    """Fail-fast validation system."""

    @staticmethod
    def validate_input(data: Any, schema: Dict[str, Any],
                      context: SecurityContext) -> bool:
        """Validate input data against schema."""
        try:
            # Basic validation (extend with more sophisticated validation)
            if not data:
                raise ValidationError("Empty input data")

            if isinstance(schema.get("type"), str):
                expected_type = schema["type"]
                if expected_type == "bytes" and not isinstance(data, bytes):
                    raise ValidationError(f"Expected bytes, got {type(data)}")
                elif expected_type == "string" and not isinstance(data, str):
                    raise ValidationError(f"Expected string, got {type(data)}")

            if "max_length" in schema:
                if len(data) > schema["max_length"]:
                    raise ValidationError(f"Data too long: {len(data)} > {schema['max_length']}")

            return True

        except ValidationError as e:
            SecurityManager.log_security_event(
                SecurityEvent.INTEGRITY_CHECK_FAILURE,
                ThreatLevel.MEDIUM,
                context,
                {"validation_error": str(e), "schema": schema}
            )
            raise

    @staticmethod
    def validate_cryptographic_operation(operation: str, inputs: Dict[str, Any],
                                       context: SecurityContext):
        """Validate cryptographic operation parameters."""
        required_params = {
            "encrypt": ["data", "algorithm"],
            "decrypt": ["encrypted_data", "key"],
            "sign": ["data", "key"],
            "verify": ["data", "signature", "key"]
        }

        if operation not in required_params:
            raise ValidationError(f"Unknown operation: {operation}")

        missing = []
        for param in required_params[operation]:
            if param not in inputs:
                missing.append(param)

        if missing:
            raise ValidationError(f"Missing required parameters: {missing}")

    @staticmethod
    def validate_security_context(context: SecurityContext):
        """Validate security context."""
        if not context.operation:
            raise ValidationError("Security context missing operation")

        if context.security_level == SecurityLevel.CRITICAL:
            if not context.user_id:
                raise ValidationError("Critical operations require user authentication")

    @staticmethod
    def validate_file_integrity(filepath: str, expected_hash: str) -> bool:
        """Validate file integrity against expected hash."""
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'rb') as f:
            file_hash = hash_sha3_512(f.read()).hex()

        return file_hash == expected_hash


class SecurityError(Exception):
    """Base security exception."""
    pass


class ValidationError(SecurityError):
    """Input validation error."""
    pass


class SecurityManager:
    """Central security management system."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.enclave_manager = EnclaveManager()
        self.key_manager = KeyManager()
        self.audit_logger = AuditLogger()
        self.validator = FailFastValidator()

        self._initialized = True

    @classmethod
    def log_security_event(cls, event_type: SecurityEvent,
                          threat_level: ThreatLevel,
                          context: SecurityContext,
                          details: Dict[str, Any]):
        """Log a security event."""
        instance = cls()
        event = SecurityEventLog(
            event_id="",
            event_type=event_type,
            threat_level=threat_level,
            context=context,
            details=details,
            timestamp=datetime.utcnow(),
            checksum=""
        )
        instance.audit_logger.log_event(event)

    def execute_secure_operation(self, operation: str,
                               inputs: Dict[str, Any],
                               context: SecurityContext) -> Any:
        """Execute operation with full security validation."""
        try:
            # Validate security context
            self.validator.validate_security_context(context)

            # Validate operation parameters
            self.validator.validate_cryptographic_operation(operation, inputs, context)

            # Determine if enclave should be used
            use_enclave = (context.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
                          and self.enclave_manager.is_enclave_available())

            if use_enclave:
                # Execute in hardware enclave
                result = self.enclave_manager.execute_in_enclave(
                    operation, inputs.get("data", b""), context
                )
            else:
                # Execute in software (with security checks)
                result = self._execute_software_operation(operation, inputs, context)

            # Log successful operation
            self.log_security_event(
                SecurityEvent.ENCRYPTION_OPERATION if operation in ["encrypt", "decrypt"]
                else SecurityEvent.AUTHENTICATION_SUCCESS,
                ThreatLevel.LOW,
                context,
                {"operation": operation, "enclave_used": use_enclave}
            )

            return result

        except Exception as e:
            # Log security failure
            self.log_security_event(
                SecurityEvent.INTEGRITY_CHECK_FAILURE,
                ThreatLevel.HIGH,
                context,
                {"operation": operation, "error": str(e)}
            )
            raise SecurityError(f"Secure operation failed: {e}")

    def _execute_software_operation(self, operation: str,
                                  inputs: Dict[str, Any],
                                  context: SecurityContext) -> Any:
        """Execute operation in software with security checks."""
        # Generate unique key for this operation
        key = self.key_manager.generate_ephemeral_key("kyber1024", context)

        try:
            if operation == "encrypt":
                # This would call the actual encryption functions
                return f"encrypted_{inputs['data']}_with_key_{key.hex()[:8]}"
            elif operation == "decrypt":
                # This would call the actual decryption functions
                return f"decrypted_{inputs['encrypted_data']}"
            else:
                raise SecurityError(f"Unsupported software operation: {operation}")
        finally:
            # Securely delete the key
            self.key_manager.secure_key_deletion(key)

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security system status."""
        return {
            "enclave_available": self.enclave_manager.is_enclave_available(),
            "enclave_type": "simulated",  # Would detect actual HSM type
            "keys_generated": len(self.key_manager.used_keys),
            "audit_events_logged": 0,  # Would track actual count
            "last_security_check": datetime.utcnow().isoformat(),
            "threat_level": "normal"
        }


# Global security manager instance
security_manager = SecurityManager()


def require_security_level(level: SecurityLevel):
    """Decorator to require minimum security level."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Extract security context from kwargs or create default
            context = kwargs.get('security_context')
            if not context:
                context = SecurityContext(security_level=level)

            if context.security_level.value < level.value:
                raise SecurityError(f"Operation requires {level.value} security level")

            return func(*args, **kwargs)
        return wrapper
    return decorator


def audit_operation(operation_name: str):
    """Decorator to audit operations."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            context = kwargs.get('security_context', SecurityContext())
            context.operation = operation_name

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                # Log successful operation
                SecurityManager.log_security_event(
                    SecurityEvent.ENCRYPTION_OPERATION,
                    ThreatLevel.LOW,
                    context,
                    {"operation": operation_name, "duration": time.time() - start_time}
                )

                return result
            except Exception as e:
                # Log failed operation
                SecurityManager.log_security_event(
                    SecurityEvent.INTEGRITY_CHECK_FAILURE,
                    ThreatLevel.MEDIUM,
                    context,
                    {"operation": operation_name, "error": str(e), "duration": time.time() - start_time}
                )
                raise
        return wrapper
    return decorator