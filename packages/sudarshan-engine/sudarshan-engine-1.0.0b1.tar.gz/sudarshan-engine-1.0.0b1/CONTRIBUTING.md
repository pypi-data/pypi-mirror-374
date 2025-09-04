# Contributing to Sudarshan Engine

Thank you for your interest in contributing to Sudarshan Engine! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Security](#security)
- [Community](#community)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- **Be respectful** and inclusive in all interactions
- **Be collaborative** and help fellow contributors
- **Be patient** with new contributors
- **Be constructive** in feedback and criticism
- **Follow the law** and respect intellectual property

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- CMake (for building liboqs)
- GCC/Clang compiler
- OpenSSL development libraries

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/your-username/sudarshan-engine.git
cd sudarshan-engine
```

3. Set up the upstream remote:

```bash
git remote add upstream https://github.com/sudarshan-engine/sudarshan-engine.git
```

## Development Setup

### Automated Setup

Run the development setup script:

```bash
# Linux/macOS
./scripts/setup_dev.sh

# Windows
scripts\setup_dev.bat
```

### Manual Setup

1. **Install system dependencies:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential cmake ninja-build libssl-dev python3-dev doxygen graphviz valgrind

# macOS
brew install cmake ninja openssl@3 doxygen graphviz astyle valgrind

# Windows (using Chocolatey)
choco install cmake ninja python3 openssl git
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Build liboqs:**

```bash
git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
make -j$(nproc)
sudo make install
sudo ldconfig  # Linux only
```

4. **Verify installation:**

```bash
python -c "import sudarshan; print('✅ Sudarshan Engine ready')"
```

## Contributing Guidelines

### Types of Contributions

- **🐛 Bug fixes** - Fix existing issues
- **✨ New features** - Add new functionality
- **📚 Documentation** - Improve documentation
- **🧪 Tests** - Add or improve tests
- **🔒 Security** - Security improvements
- **⚡ Performance** - Performance optimizations
- **🎨 Code style** - Code formatting and style improvements

### Commit Message Format

Use clear, descriptive commit messages following this format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

**Examples:**
```
feat(crypto): add Kyber1024 key encapsulation support

fix(spq_format): resolve header parsing bug in compressed files

docs(api): update crypto module documentation

test(security): add penetration testing for injection attacks
```

### Branch Naming

Use descriptive branch names:

```
feature/add-kyber-support
bugfix/header-parsing-issue
docs/update-api-reference
test/add-security-tests
```

## Development Workflow

### 1. Choose an Issue

- Check the [GitHub Issues](https://github.com/sudarshan-engine/sudarshan-engine/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write clear, concise code
- Add tests for new functionality
- Update documentation as needed
- Follow the existing code style

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/security/

# Run with coverage
pytest --cov=sudarshan --cov-report=html

# Run linting
flake8 sudarshan/ tests/
black --check sudarshan/ tests/
```

### 5. Commit Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new quantum-safe feature

- Implements Kyber key encapsulation
- Adds comprehensive test coverage
- Updates documentation"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the pull request template
5. Request review from maintainers

## Testing

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Security tests
pytest tests/security/

# With coverage
pytest --cov=sudarshan --cov-report=html

# Specific test file
pytest tests/unit/test_crypto.py

# Specific test function
pytest tests/unit/test_crypto.py::test_kyber_keygen
```

### Writing Tests

**Test Structure:**
```python
import pytest
from sudarshan import spq_create, spq_read

class TestSPQOperations:
    def test_basic_encryption_decryption(self):
        """Test basic SPQ file creation and reading."""
        # Arrange
        test_data = b"Hello, Quantum World!"
        password = "test_password"
        metadata = {"test": True}

        # Act
        result = spq_create("test.spq", metadata, test_data, password)

        # Assert
        assert result["filepath"] == "test.spq"
        assert result["algorithm"] == "kyber1024"

        # Verify decryption
        decrypted = spq_read("test.spq", password)
        assert decrypted["payload"] == test_data
        assert decrypted["metadata"]["test"] == True
```

**Test Categories:**
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Security Tests**: Test security properties and attack resistance
- **Performance Tests**: Test performance characteristics
- **Fuzzing Tests**: Test input validation and edge cases

### Test Coverage

Maintain test coverage above 85%:

```bash
# Check coverage
pytest --cov=sudarshan --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=sudarshan --cov-report=html
open htmlcov/index.html
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme myst-parser

# Build HTML documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Documentation Guidelines

- **Use reStructuredText (.rst)** for main documentation
- **Use MyST Markdown** for tutorials and guides
- **Include code examples** for all major features
- **Document security considerations** for cryptographic functions
- **Provide API reference** for all public interfaces

### Documentation Structure

```
docs/
├── index.rst              # Main documentation page
├── installation.rst       # Installation guide
├── quickstart.rst         # Quick start guide
├── architecture.md        # System architecture
├── tutorials/             # Tutorial guides
│   ├── wallet_integration.rst
│   └── database_security.rst
├── api/                   # API reference
│   └── crypto.rst
├── security/              # Security documentation
│   └── threat_model.rst
└── guides/                # User guides
    ├── cli_usage.rst
    └── desktop_app.rst
```

## Security

### Security Considerations

- **Never commit secrets** or private keys
- **Use strong passwords** for testing
- **Report security issues** responsibly
- **Follow secure coding practices**

### Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report security issues by emailing:
**security@sudarshan.engine**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fixes (optional)

### Security Testing

```bash
# Run security tests
pytest tests/security/

# Run fuzzing tests
pytest tests/fuzzing/

# Check for common vulnerabilities
bandit -r sudarshan/
safety check
```

## Code Style

### Python Style

Follow PEP 8 with these tools:

```bash
# Code formatting
black sudarshan/ tests/

# Import sorting
isort sudarshan/ tests/

# Linting
flake8 sudarshan/ tests/

# Type checking
mypy sudarshan/
```

### Code Style Guidelines

- **Use type hints** for all function parameters and return values
- **Write docstrings** for all public functions and classes
- **Use descriptive variable names** (avoid single letters except in loops)
- **Keep functions small** and focused on single responsibilities
- **Use meaningful commit messages** and branch names
- **Add comments** for complex logic

### Example Code Style

```python
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuantumSafeCrypto:
    """Quantum-safe cryptographic operations."""

    def __init__(self, algorithm: str = "kyber1024") -> None:
        """
        Initialize quantum-safe crypto.

        Args:
            algorithm: The PQC algorithm to use

        Raises:
            ValueError: If algorithm is not supported
        """
        self.algorithm = algorithm
        self._validate_algorithm(algorithm)
        logger.info(f"Initialized with algorithm: {algorithm}")

    def _validate_algorithm(self, algorithm: str) -> None:
        """Validate that the algorithm is supported."""
        supported = ["kyber512", "kyber768", "kyber1024"]
        if algorithm not in supported:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def encrypt_data(
        self,
        data: bytes,
        public_key: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Encrypt data using quantum-safe algorithms.

        Args:
            data: The plaintext data to encrypt
            public_key: The recipient's public key
            metadata: Optional metadata to include

        Returns:
            Dictionary containing encrypted data and metadata

        Raises:
            CryptoError: If encryption fails
        """
        try:
            # Implementation here
            result = {
                "encrypted_data": b"encrypted_data",
                "algorithm": self.algorithm,
                "metadata": metadata or {}
            }
            logger.info(f"Successfully encrypted {len(data)} bytes")
            return result
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise CryptoError(f"Encryption failed: {e}") from e
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Slack**: Real-time chat (#general, #development, #security)
- **Discord**: Community chat and support

### Getting Help

1. **Check the documentation** first
2. **Search existing issues** on GitHub
3. **Ask in Discussions** for general questions
4. **Use Slack/Discord** for real-time help
5. **Create an issue** for bugs or feature requests

### Recognition

Contributors are recognized through:
- **GitHub contributor statistics**
- **Mention in release notes**
- **Contributor spotlight** in community updates
- **Digital badges** for significant contributions

### Governance

The project follows these governance principles:

- **Open and transparent** decision making
- **Merit-based** contribution acceptance
- **Inclusive** community participation
- **Security-first** approach to all changes
- **Regular** community feedback collection

## License

By contributing to Sudarshan Engine, you agree that your contributions will be licensed under the same license as the project (AGPLv3 for open-source components).

## Recognition

Thank you for contributing to Sudarshan Engine! Your contributions help make quantum-safe cryptography accessible to everyone.

**Contributors:**
- See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full list
- Check [GitHub Contributors](https://github.com/sudarshan-engine/sudarshan-engine/graphs/contributors)

---

**Ready to contribute?** Start by exploring the issues and picking one that interests you. Don't hesitate to ask questions in our community channels!

For more information, visit our [Community Page](https://community.sudarshan.engine).