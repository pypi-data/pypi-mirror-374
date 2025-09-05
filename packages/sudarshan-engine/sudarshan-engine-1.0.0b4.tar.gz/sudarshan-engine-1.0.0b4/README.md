# Sudarshan Engine

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Beta Version](https://img.shields.io/badge/version-beta-orange.svg)](https://github.com/Yash-Sharma1810/sudarshan-engine)
[![GitHub Issues](https://img.shields.io/github/issues/Yash-Sharma1810/sudarshan_engine)](https://github.com/Yash-Sharma1810/sudarshan_engine/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Yash-Sharma1810/sudarshan_engine)](https://github.com/Yash-Sharma1810/sudarshan_engine/stargazers)

**Universal Quantum-Safe Cybersecurity Engine** 🚀

Sudarshan Engine is a comprehensive, open-core cybersecurity solution that provides quantum-resistant protection for any digital asset or application. Built with a unique "Box-in-a-Box" architecture, it offers unparalleled security against current and future threats.

> **⚠️ BETA VERSION**: This is a beta release. Please report any issues or bugs you encounter.

## Overview

### Key Features
- **🛡️ Quantum-Safe**: NIST-approved PQC algorithms (Kyber, Dilithium, Falcon) when available
- **🔄 Universal**: Secures wallets, databases, payment systems, and any digital service
- **📦 Box-in-a-Box**: Four-layer security model with independent protections
- **📁 .spq Format**: Proprietary quantum-safe file format for encrypted data
- **💰 Freemium**: Free tier with premium enterprise features
- **🔧 Multi-Platform**: Linux, macOS, Windows support
- **📚 Core Engine**: Focused quantum-safe cryptography library

> **⚠️ IMPORTANT**: Quantum-safe features require liboqs library. Falls back to classical cryptography if unavailable.

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Sudarshan Engine                         │
├─────────────────────────────────────────────────────────────┤
│ Transaction Capsule  ← One-time PQC operations             │
│ Isolation Room       ← Hardware-secured gateway            │
│ Outer Vault          ← Multi-factor PQC vault              │
│ Inner Shield         ← PQC wrapper for legacy assets       │
│ .spq File Format     ← Quantum-safe encrypted files        │
│ Core Crypto Engine   ← Kyber + Dilithium + AES/ChaCha20    │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Install from PyPI (Latest Stable)
pip install sudarshan-engine

# For latest beta features
pip install sudarshan-engine --pre

# Or clone and install from source
git clone https://github.com/Yash-Sharma1810/sudarshan_engine.git
cd sudarshan_engine
pip install -e .
```

### Production Deployment

For production environments, see our comprehensive [Production Deployment Guide](PRODUCTION_DEPLOYMENT.md) which covers:

- 🔧 **liboqs Installation** for full quantum-safe capabilities
- 🛡️ **Security Audit** using built-in tools
- 📊 **Monitoring** security events and performance
- 🔄 **Dependency Management** with automated scanning
- ⚙️ **Configuration** best practices

**Quick Production Setup:**
```bash
# 1. Install with full PQC support
pip install sudarshan-engine

# 2. Install liboqs (recommended)
sudo apt-get install liboqs-dev  # Ubuntu/Debian

# 3. Run security audit
python -c "from sudarshan.security.security_audit import SecurityAuditor; auditor = SecurityAuditor('.'); print(auditor.audit())"

# 4. Configure monitoring
from sudarshan.monitoring import SecurityMonitor
monitor = SecurityMonitor()
monitor.start_monitoring()
```

### Basic Usage

**Encrypt a file:**
```bash
sudarshan spq_create --input secret.txt --output secret.spq --password mypassword
```

**Decrypt a file:**
```bash
sudarshan spq_read --input secret.spq --password mypassword
```

**Python SDK:**
```python
from sudarshan import spq_create, spq_read

# Encrypt
result = spq_create("secret.spq", {"purpose": "confidential"}, b"secret data", "password")

# Decrypt
data = spq_read("secret.spq", "password")
print(data['payload'].decode())
```

## Use Cases

### 🏦 Cryptocurrency Wallets
Protect Bitcoin, Ethereum, and other crypto wallets with quantum-safe encryption.

```python
from sudarshan import spq_create

# Secure wallet backup
wallet_data = {
    "bitcoin_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "private_key": "L1uyy5qTuGrVXrmrsvHWHgVzW9kKdrp27wBC7Vs6nZDTF2BRUVs",
    "seed_phrase": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
}

metadata = {
    "wallet_type": "bitcoin",
    "backup_date": "2025-09-02",
    "security_level": "maximum"
}

spq_create("bitcoin_wallet.spq", metadata, json.dumps(wallet_data).encode(), "secure_password")
```

### 🗄️ Database Security
Encrypt sensitive database fields and backups.

```python
# Encrypt PII data
sensitive_data = {
    "customers": [
        {
            "id": 1,
            "name": "John Doe",
            "ssn": "123-45-6789",
            "credit_card": "4111111111111111"
        }
    ]
}

metadata = {
    "data_type": "pii",
    "compliance": ["GDPR", "HIPAA"],
    "retention": "7_years"
}

spq_create("customer_pii.spq", metadata, json.dumps(sensitive_data).encode(), "db_password")
```

### 💳 Payment Systems
Secure transaction data and payment processing.

```python
# Secure payment transaction
transaction = {
    "amount": "99.99",
    "currency": "USD",
    "recipient": "merchant@example.com",
    "card_token": "tok_1A2B3C4D5E6F7G8H9I0J",
    "timestamp": "2025-09-02T11:36:58Z"
}

metadata = {
    "transaction_type": "payment",
    "compliance": ["PCI_DSS"],
    "one_time_use": True
}

spq_create("payment_tx.spq", metadata, json.dumps(transaction).encode(), "payment_key")
```

## .spq File Format

The .spq format provides quantum-safe encryption with:

- **Magic Bytes**: "SUDARSHA" identifier
- **Header**: Version, algorithm, compression info
- **Metadata**: JSON/CBOR human-readable information
- **Encrypted Payload**: Kyber KEM + AES/ChaCha20 encryption (falls back to AES/ChaCha20 only when PQC unavailable)
- **Integrity Hash**: SHA3-512 tamper detection
- **PQC Signature**: Dilithium/Falcon authentication (falls back to no signature when PQC unavailable)

## Security Features

### Quantum Resistance
- ✅ Kyber Key Encapsulation (NIST FIPS 203) - when liboqs available
- ✅ Dilithium Digital Signatures (NIST FIPS 205) - when liboqs available
- ✅ Falcon Alternative Signatures (NIST FIPS 206) - when liboqs available
- ✅ SHA3-512 Cryptographic Hashing
- ⚠️ Falls back to AES-256-GCM/ChaCha20-Poly1305 when PQC unavailable

### Defense in Depth
- ✅ Multi-layer Box-in-a-Box architecture
- ✅ Hardware security module integration
- ✅ Multi-factor authentication support
- ✅ Stateless one-time operations

### Compliance
- ✅ GDPR (General Data Protection Regulation)
- ✅ HIPAA (Health Insurance Portability)
- ✅ PCI DSS (Payment Card Industry)
- ✅ SOX (Sarbanes-Oxley)

## Installation Options

### PyPI (Recommended)
```bash
pip install sudarshan-engine
```

### Docker
```bash
docker pull yashsharma1810/sudarshan-engine:beta
docker run -it yashsharma1810/sudarshan-engine:beta
```

### From Source
```bash
git clone https://github.com/Yash-Sharma1810/sudarshan-engine.git
cd sudarshan-engine
pip install -e .
```

## Documentation

📚 **Complete Documentation**: https://docs.sudarshanengine.xyz/

### Key Sections
- [Installation Guide](docs/installation.rst)
- [Quick Start Guide](docs/quickstart.rst)
- [API Reference](docs/api/crypto.rst)
- [Architecture Overview](docs/architecture.md)
- [Security Guide](docs/security/threat_model.rst)
- [Tutorials](docs/tutorials/)

## Community & Support

### Get Help
- 📖 [Documentation](https://docs.sudarshanengine.xyz/)
- 🐛 [GitHub Issues](https://github.com/Yash-Sharma1810/sudarshan_engine/issues)
- 💬 [GitHub Discussions](https://github.com/Yash-Sharma1810/sudarshan_engine/discussions)
- 📧 [Email Support](mailto:yash02.prof@gmail.com)

### Contributing
We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Fork, clone, and contribute
git clone https://github.com/Yash-Sharma1810/sudarshan_engine.git
cd sudarshan_engine
```

### Development Status
- ✅ Core encryption engine
- ✅ .spq file format
- ✅ CLI interface
- ✅ Python SDK
- ✅ API daemon
- ✅ Testing framework
- ✅ CI/CD pipelines
- ✅ Documentation
- 🚧 Enterprise features (coming soon)

## Roadmap

### Beta Phase (Current)
- [x] Core quantum-safe encryption
- [x] .spq file format specification
- [x] Multi-platform CLI
- [x] Python SDK
- [x] Comprehensive testing
- [x] Documentation

### v1.0 Release (Q4 2025)
- [ ] Enterprise API
- [ ] Hardware security integration
- [ ] Advanced compliance features
- [ ] Performance optimizations
- [ ] Third-party security audit

### Future Releases
- [ ] Mobile applications
- [ ] Cloud integration
- [ ] Advanced threat detection
- [ ] AI-powered security features

## License

### Open-Source Components (AGPL v3.0)
- CLI interface
- Python SDK
- Core documentation
- Community tools

### Commercial Components
- Enterprise API
- Advanced security features
- Premium support
- Custom integrations

## Security

### Security Audit & Compliance
Sudarshan Engine includes comprehensive security auditing capabilities:

```bash
# Run automated security audit
python security/security_audit.py
```

**Security Features:**
- ✅ Automated security scanning (CI/CD integrated)
- ✅ Constant-time cryptographic operations
- ✅ Enhanced entropy validation for key derivation
- ✅ Secure key management with warnings for insecure storage
- ✅ Comprehensive logging for security diagnostics
- ✅ File permission and dependency vulnerability checks

### Quantum-Safe Implementation
- **When liboqs available:** Full NIST PQC algorithms (Kyber, Dilithium, Falcon)
- **Fallback mode:** AES-256-GCM/ChaCha20-Poly1305 with security warnings
- **Hybrid approach:** Combines PQC with traditional crypto when needed

### Reporting Vulnerabilities
Please report security issues responsibly:

1. **Do not** create public GitHub issues for security vulnerabilities
2. Email security issues to: **yash02.prof@gmail.com**
3. Include detailed reproduction steps and impact assessment
4. Allow 90 days for fixes before public disclosure

### Security Best Practices
- Regular automated security audits via GitHub Actions
- Dependency vulnerability scanning
- CodeQL security analysis
- Secure random generation validation
- Timing attack protection with constant-time operations

## Performance

### Benchmarks (Approximate)
- **File Encryption**: ~50 MB/s (Kyber-1024 + AES-256-GCM)
- **File Decryption**: ~100 MB/s
- **Signature Generation**: ~2 ms (Dilithium5)
- **Signature Verification**: ~1 ms
- **Key Generation**: ~10 ms (Kyber-1024)

### System Requirements
- **CPU**: 64-bit processor with AES-NI support (recommended)
- **RAM**: 512 MB minimum, 2 GB recommended
- **Storage**: 100 MB for installation
- **Network**: Internet connection for updates

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Latest Beta Changes
- ✨ Complete quantum-safe encryption engine
- 🏗️ Box-in-a-Box security architecture
- 📁 .spq file format implementation
- 🔧 Comprehensive CLI tools
- 📚 Extensive documentation
- 🧪 Full test suite with CI/CD

## Acknowledgments

- **NIST**: For PQC algorithm standardization
- **Open Quantum Safe**: For liboqs library
- **Python Cryptography Community**: For security best practices
- **Beta Testers**: For valuable feedback and bug reports

## Contact

- **Project Lead**: Yash Sharma
- **GitHub**: [@Yash-Sharma1810](https://github.com/Yash-Sharma1810)
- **Email**: yash02.prof@gmail.com
- **Website**: https://sudarshanengine.xyz
- **LinkedIn**: [Yash Sharma](https://linkedin.com/in/yashsharma2652)

---

**🚀 Ready to secure your digital assets against quantum threats?**

[Get Started](docs/quickstart.rst) | [Documentation](https://docs.sudarshanengine.xyz/) | [GitHub](https://github.com/Yash-Sharma1810/sudarshan_engine)

*Sudarshan Engine - Protecting the future of digital security* 🛡️