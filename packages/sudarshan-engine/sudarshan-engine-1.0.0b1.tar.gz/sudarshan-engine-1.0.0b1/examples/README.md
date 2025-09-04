# Sudarshan Engine Examples

A comprehensive collection of examples demonstrating the Sudarshan Engine's quantum-safe capabilities, from basic usage to advanced integrations.

## 📚 Example Categories

### 🔰 Basic Usage
- **basic_usage.py** - Fundamental .spq file operations
- **simple_encryption.py** - Basic encryption/decryption examples
- **file_operations.py** - File-based .spq operations

### 🔧 Advanced Usage
- **advanced_usage.py** - Custom algorithms and compression
- **batch_operations.py** - Processing multiple files
- **streaming_encryption.py** - Large file handling

### 🔐 Security Protocols
- **inner_shield_example.py** - Legacy asset protection
- **outer_vault_example.py** - Multi-factor authentication
- **isolation_room_example.py** - Hardware security
- **transaction_capsule_example.py** - One-time transactions

### 💰 Integration Examples
- **wallet_integration.py** - Cryptocurrency wallet protection
- **database_encryption.py** - Database field encryption
- **api_security.py** - API request/response protection
- **file_sharing.py** - Secure file sharing

### 🌐 Web & Desktop
- **web_app_example.py** - Web application integration
- **desktop_app_example.py** - Desktop application integration
- **rest_api_example.py** - REST API integration

## 🚀 Quick Start

### 1. Install Sudarshan Engine

```bash
pip install sudarshan-engine
```

### 2. Run Basic Examples

```bash
cd examples

# Run basic usage examples
python basic_usage.py

# Run advanced examples
python advanced_usage.py

# Run security protocol examples
python inner_shield_example.py
```

### 3. Explore Integration Examples

```bash
# Wallet integration
python wallet_integration.py

# Database encryption
python database_encryption.py

# API security
python api_security.py
```

## 📋 Prerequisites

- Python 3.8+
- Sudarshan Engine installed
- Basic understanding of cryptography concepts

## 🎯 Example Structure

Each example follows a consistent structure:

```python
#!/usr/bin/env python3
"""
Example: [Brief Description]

This example demonstrates [specific functionality].
"""

# Imports
from sudarshan import spq_create, spq_read
# ... other imports

# Configuration
# ... setup variables

# Main demonstration
def main():
    # Step-by-step implementation
    # Clear comments and error handling
    pass

if __name__ == "__main__":
    main()
```

## 🔍 Key Concepts Demonstrated

### Basic Operations
- Creating and reading .spq files
- Metadata handling (JSON/CBOR)
- Algorithm selection (Kyber, Dilithium variants)
- Compression options (Zstd, LZ4, none)

### Security Features
- Quantum-safe encryption (PQC algorithms)
- Integrity verification (SHA3-512 hashes)
- Authentication (PQC signatures)
- Tamper detection and recovery

### Advanced Features
- Custom metadata schemas
- Batch processing
- Error handling and recovery
- Performance optimization

### Integration Patterns
- File system integration
- Database integration
- Network/API integration
- Hardware security integration

## 🧪 Testing Examples

Run the test suite to verify examples work correctly:

```bash
# Run all example tests
python -m pytest tests/ -k "example"

# Run specific example tests
python -m pytest tests/test_basic_usage.py -v

# Run integration tests
python -m pytest tests/integration/ -v
```

## 📖 Documentation

### API Reference
- [Sudarshan Engine API Docs](https://docs.sudarshan-engine.org/api)
- [PQC Algorithm Reference](https://docs.sudarshan-engine.org/crypto)
- [.spq Format Specification](https://docs.sudarshan-engine.org/spq-format)

### Security Guidelines
- [Security Best Practices](https://docs.sudarshan-engine.org/security)
- [Threat Model](https://docs.sudarshan-engine.org/threat-model)
- [Compliance Guide](https://docs.sudarshan-engine.org/compliance)

## 🤝 Contributing Examples

### Adding New Examples

1. **Choose a category** - Basic, Advanced, Security, or Integration
2. **Follow the structure** - Use the standard template
3. **Add comprehensive comments** - Explain each step
4. **Include error handling** - Show proper exception handling
5. **Add tests** - Create corresponding test cases
6. **Update documentation** - Add to this README

### Example Template

```python
#!/usr/bin/env python3
"""
Example: [Descriptive Title]

[Brief description of what this example demonstrates]

Prerequisites:
- [Any special requirements]

Expected Output:
- [What the user should see when running this example]
"""

# Implementation here
```

### Testing Guidelines

- Test both success and failure scenarios
- Verify cryptographic operations
- Test edge cases and error conditions
- Ensure examples are self-contained
- Include performance benchmarks where relevant

## 🚨 Security Notes

### Key Management
- Never hardcode keys in examples
- Use secure key generation for demonstrations
- Demonstrate proper key lifecycle management

### Data Handling
- Use test data only
- Avoid real sensitive information
- Demonstrate secure data disposal

### Error Handling
- Show proper exception handling
- Demonstrate secure failure modes
- Include logging best practices

## 📊 Performance Benchmarks

Example performance characteristics (approximate):

| Operation | File Size | Time | Memory |
|-----------|-----------|------|--------|
| Encrypt 1MB | 1MB | ~50ms | ~5MB |
| Decrypt 1MB | 1MB | ~30ms | ~3MB |
| Key Generation | - | ~10ms | ~1MB |
| Batch (100 files) | 100MB | ~3s | ~50MB |

*Benchmarks run on Intel i7-9750H, results may vary*

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure Sudarshan Engine is installed
pip install sudarshan-engine

# Check Python version
python --version  # Should be 3.8+
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x examples/*.py

# Run with appropriate permissions
sudo python examples/admin_example.py
```

**Memory Issues**
```bash
# For large files, increase memory limits
export PYTHON_MAX_MEM=4GB
python examples/large_file_example.py
```

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/sudarshan-engine/sudarshan-engine/issues)
- **Documentation**: [Read the docs](https://docs.sudarshan-engine.org)
- **Community**: [Join Discord](https://discord.gg/sudarshan-engine)

## 📄 License

These examples are part of the Sudarshan Engine project and follow the same AGPL-3.0 license.

## 🙏 Acknowledgments

- Examples contributed by the Sudarshan Engine community
- Special thanks to early adopters and beta testers
- Inspired by real-world quantum-safe implementation needs

---

**Ready to explore quantum-safe cryptography? Let's get started! 🚀**