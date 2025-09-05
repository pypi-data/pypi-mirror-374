Crypto API Reference
====================

Core cryptographic functions and quantum-safe algorithms.

.. contents::
   :local:
   :depth: 2

QuantumSafeCrypto Class
=======================

Main cryptographic interface for quantum-safe operations.

.. autoclass:: sudarshan.crypto.QuantumSafeCrypto
   :members:
   :undoc-members:
   :show-inheritance:

Key Encapsulation Methods
=========================

Kyber Key Encapsulation Mechanism (KEM) implementation.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.kyber_keygen

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.kyber_encapsulate

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.kyber_decapsulate

Digital Signature Methods
=========================

Dilithium and Falcon digital signature implementations.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.dilithium_keygen

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.dilithium_sign

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.dilithium_verify

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.falcon_keygen

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.falcon_sign

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.falcon_verify

Symmetric Encryption Methods
============================

AES-256-GCM and ChaCha20-Poly1305 implementations.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.aes_encrypt

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.aes_decrypt

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.chacha_encrypt

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.chacha_decrypt

Hash Functions
==============

SHA3-512 and other cryptographic hash functions.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.sha3_512

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.sha3_256

Key Derivation Functions
========================

HKDF and other key derivation implementations.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.hkdf_derive

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.pbkdf2_derive

Random Number Generation
========================

Cryptographically secure random number generation.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.random_bytes

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.random_int

Algorithm Information
=====================

Get information about supported algorithms and their parameters.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.get_algorithm_info

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.list_supported_algorithms

Security Level Assessment
=========================

Assess the security level of cryptographic operations.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.assess_security_level

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.get_quantum_resistance

Performance Metrics
===================

Get performance metrics for cryptographic operations.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.get_performance_metrics

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.benchmark_algorithm

Error Handling
==============

Cryptographic operation error handling and validation.

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.validate_key

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.validate_signature

.. automethod:: sudarshan.crypto.QuantumSafeCrypto.get_last_error

SPQ Format Module
=================

.spq file format handling and serialization.

.. automodule:: sudarshan.spq_format
   :members:
   :undoc-members:
   :show-inheritance:

SPQ Creation Functions
======================

Create .spq files with quantum-safe encryption.

.. autofunction:: sudarshan.spq_format.create_spq_file

.. autofunction:: sudarshan.spq_format.write_spq_header

.. autofunction:: sudarshan.spq_format.write_spq_metadata

.. autofunction:: sudarshan.spq_format.write_spq_payload

.. autofunction:: sudarshan.spq_format.write_spq_hash

.. autofunction:: sudarshan.spq_format.write_spq_signature

SPQ Reading Functions
=====================

Read and decrypt .spq files.

.. autofunction:: sudarshan.spq_format.read_spq_file

.. autofunction:: sudarshan.spq_format.read_spq_header

.. autofunction:: sudarshan.spq_format.read_spq_metadata

.. autofunction:: sudarshan.spq_format.read_spq_payload

.. autofunction:: sudarshan.spq_format.verify_spq_hash

.. autofunction:: sudarshan.spq_format.verify_spq_signature

SPQ Utility Functions
=====================

Utility functions for .spq file operations.

.. autofunction:: sudarshan.spq_format.get_spq_info

.. autofunction:: sudarshan.spq_format.validate_spq_format

.. autofunction:: sudarshan.spq_format.compress_payload

.. autofunction:: sudarshan.spq_format.decompress_payload

Protocol Modules
================

Box-in-a-Box security protocol implementations.

Inner Shield Protocol
=====================

PQC wrapper for legacy assets.

.. automodule:: sudarshan.protocols.inner_shield
   :members:
   :undoc-members:
   :show-inheritance:

Outer Vault Protocol
====================

Multi-factor authentication and access control.

.. automodule:: sudarshan.protocols.outer_vault
   :members:
   :undoc-members:
   :show-inheritance:

Isolation Room Protocol
=======================

Hardware-secured cryptographic operations.

.. automodule:: sudarshan.protocols.isolation_room
   :members:
   :undoc-members:
   :show-inheritance:

Transaction Capsule Protocol
============================

One-time stateless cryptographic operations.

.. automodule:: sudarshan.protocols.transaction_capsule
   :members:
   :undoc-members:
   :show-inheritance:

Security Module
===============

Security management and monitoring.

.. automodule:: security.security_manager
   :members:
   :undoc-members:
   :show-inheritance:

Security Context
================

Security context management for operations.

.. autoclass:: security.security_manager.SecurityContext
   :members:
   :undoc-members:
   :show-inheritance:

Security Level
==============

Security level definitions and assessment.

.. autoclass:: security.security_manager.SecurityLevel
   :members:
   :undoc-members:
   :show-inheritance:

Penetration Testing
===================

Security testing and vulnerability assessment.

.. automodule:: security.penetration_testing
   :members:
   :undoc-members:
   :show-inheritance:

Fuzzing Engine
==============

Input fuzzing and mutation testing.

.. autoclass:: security.penetration_testing.FuzzingEngine
   :members:
   :undoc-members:
   :show-inheritance:

Attack Simulator
================

Attack simulation and testing.

.. autoclass:: security.penetration_testing.AttackSimulator
   :members:
   :undoc-members:
   :show-inheritance:

Vulnerability Scanner
=====================

Automated vulnerability scanning.

.. autoclass:: security.penetration_testing.VulnerabilityScanner
   :members:
   :undoc-members:
   :show-inheritance:

Security Monitoring
===================

Real-time security monitoring and alerting.

.. autoclass:: security.penetration_testing.SecurityMonitoring
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions and Error Handling
=============================

Custom exceptions for Sudarshan Engine.

.. automodule:: sudarshan.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Cryptographic Exceptions
========================

.. autoexception:: sudarshan.exceptions.CryptoError

.. autoexception:: sudarshan.exceptions.KeyError

.. autoexception:: sudarshan.exceptions.SignatureError

.. autoexception:: sudarshan.exceptions.EncryptionError

.. autoexception:: sudarshan.exceptions.DecryptionError

Protocol Exceptions
===================

.. autoexception:: sudarshan.exceptions.ProtocolError

.. autoexception:: sudarshan.exceptions.AuthenticationError

.. autoexception:: sudarshan.exceptions.AuthorizationError

File Format Exceptions
======================

.. autoexception:: sudarshan.exceptions.SP QFileError

.. autoexception:: sudarshan.exceptions.SP QFormatError

.. autoexception:: sudarshan.exceptions.SP QValidationError

Security Exceptions
===================

.. autoexception:: security.exceptions.SecurityError

.. autoexception:: security.exceptions.VulnerabilityError

.. autoexception:: security.exceptions.ComplianceError

Constants and Configuration
===========================

Algorithm constants and configuration options.

.. automodule:: sudarshan.constants
   :members:
   :undoc-members:
   :show-inheritance:

Algorithm Identifiers
=====================

.. autodata:: sudarshan.constants.ALGORITHM_KYBER512

.. autodata:: sudarshan.constants.ALGORITHM_KYBER768

.. autodata:: sudarshan.constants.ALGORITHM_KYBER1024

.. autodata:: sudarshan.constants.ALGORITHM_DILITHIUM2

.. autodata:: sudarshan.constants.ALGORITHM_DILITHIUM3

.. autodata:: sudarshan.constants.ALGORITHM_DILITHIUM5

.. autodata:: sudarshan.constants.ALGORITHM_FALCON512

.. autodata:: sudarshan.constants.ALGORITHM_FALCON1024

Compression Algorithms
======================

.. autodata:: sudarshan.constants.COMPRESSION_NONE

.. autodata:: sudarshan.constants.COMPRESSION_ZSTD

.. autodata:: sudarshan.constants.COMPRESSION_LZ4

.. autodata:: sudarshan.constants.COMPRESSION_BROTLI

Security Levels
===============

.. autodata:: sudarshan.constants.SECURITY_LEVEL_BASIC

.. autodata:: sudarshan.constants.SECURITY_LEVEL_STANDARD

.. autodata:: sudarshan.constants.SECURITY_LEVEL_HIGH

.. autodata:: sudarshan.constants.SECURITY_LEVEL_CRITICAL

File Permissions
================

.. autodata:: sudarshan.constants.FILE_PERMISSION_RESTRICTED

.. autodata:: sudarshan.constants.FILE_PERMISSION_PRIVATE

.. autodata:: sudarshan.constants.FILE_PERMISSION_PUBLIC

Type Definitions
================

Type hints and custom types used throughout the codebase.

.. automodule:: sudarshan.types
   :members:
   :undoc-members:
   :show-inheritance:

Key Types
==========

.. autodata:: sudarshan.types.PublicKey

.. autodata:: sudarshan.types.PrivateKey

.. autodata:: sudarshan.types.SharedSecret

.. autodata:: sudarshan.types.Signature

Data Types
==========

.. autodata:: sudarshan.types.EncryptedData

.. autodata:: sudarshan.types.PlaintextData

.. autodata:: sudarshan.types.MetadataDict

.. autodata:: sudarshan.types.SP QHeader

Configuration Types
===================

.. autodata:: sudarshan.types.CryptoConfig

.. autodata:: sudarshan.types.SecurityConfig

.. autodata:: sudarshan.types.ProtocolConfig

Utility Functions
=================

General utility functions and helpers.

.. automodule:: sudarshan.utils
   :members:
   :undoc-members:
   :show-inheritance:

Data Validation
===============

.. autofunction:: sudarshan.utils.validate_metadata

.. autofunction:: sudarshan.utils.validate_password_strength

.. autofunction:: sudarshan.utils.validate_file_path

.. autofunction:: sudarshan.utils.validate_algorithm

Cryptographic Utilities
=======================

.. autofunction:: sudarshan.utils.generate_nonce

.. autofunction:: sudarshan.utils.generate_timestamp

.. autofunction:: sudarshan.utils.calculate_file_hash

.. autofunction:: sudarshan.utils.secure_delete_file

Encoding and Decoding
=====================

.. autofunction:: sudarshan.utils.base64_encode

.. autofunction:: sudarshan.utils.base64_decode

.. autofunction:: sudarshan.utils.hex_encode

.. autofunction:: sudarshan.utils.hex_decode

.. autofunction:: sudarshan.utils.json_serialize

.. autofunction:: sudarshan.utils.json_deserialize

Performance Utilities
=====================

.. autofunction:: sudarshan.utils.measure_execution_time

.. autofunction:: sudarshan.utils.get_memory_usage

.. autofunction:: sudarshan.utils.get_cpu_usage

.. autofunction:: sudarshan.utils.benchmark_function

Logging and Debugging
=====================

.. autofunction:: sudarshan.utils.setup_logging

.. autofunction:: sudarshan.utils.get_logger

.. autofunction:: sudarshan.utils.log_crypto_operation

.. autofunction:: sudarshan.utils.log_security_event

.. autofunction:: sudarshan.utils.enable_debug_mode

.. autofunction:: sudarshan.utils.disable_debug_mode