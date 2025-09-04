# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-beta.1] - 2025-09-02

### Added
- Initial beta release of Sudarshan Engine
- Quantum-safe encryption algorithms (Kyber, Dilithium, Falcon)
- Box-in-a-Box security architecture
- SPQ file format with PQC protection
- Multi-platform GUI applications
- Enterprise API daemon
- Comprehensive testing framework
- Documentation and examples

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Implemented post-quantum cryptography protection
- Secure key management and storage
- Audit logging for security events

## [1.0.0-beta.2] - 2025-09-04

### Security
- **CRITICAL**: Removed hardcoded private keys from repository
- **CRITICAL**: Clarified false quantum-safe claims with proper fallback documentation
- **HIGH**: Implemented constant-time cryptographic operations to prevent timing attacks
- **HIGH**: Enhanced entropy validation for key derivation (32+ bytes recommended)
- **MEDIUM**: Added comprehensive security logging and diagnostics
- **MEDIUM**: Implemented automated security audit system
- **MEDIUM**: Added CI/CD security checks with GitHub Actions
- **MEDIUM**: Improved key management with security warnings for insecure storage

### Added
- Security audit script (`security/security_audit.py`)
- GitHub Actions workflow for automated security scanning
- Constant-time comparison functions for cryptographic operations
- Enhanced entropy quality checks
- Comprehensive security documentation

### Changed
- Updated README.md to clearly document PQC availability requirements
- Enhanced error messages and security warnings
- Improved fallback behavior documentation

### Fixed
- Timing attack vulnerabilities in hash comparisons
- Insufficient entropy validation in key derivation
- Missing security checks in CI/CD pipeline

## [Unreleased]

### Added
- Additional quantum-safe algorithms
- Performance optimizations
- Enhanced documentation

### Fixed
- Bug fixes and improvements

---

For more details, see the [GitHub repository](https://github.com/Yash-Sharma1810/sudarshan_engine).