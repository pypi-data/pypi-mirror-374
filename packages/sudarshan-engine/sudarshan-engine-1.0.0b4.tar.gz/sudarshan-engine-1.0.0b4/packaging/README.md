# Sudarshan Engine Packaging & Distribution

This directory contains all the tools and scripts needed to build, package, and distribute the Sudarshan Engine across multiple platforms and distribution channels.

## 📦 Distribution Channels

### 1. PyPI (Python Package Index)
**Target**: Python developers, automated deployments
**Components**: Core engine, CLI, SDK
**License**: AGPL-3.0

### 2. Native Packages
**Target**: End users, system administrators
- **Linux**: Debian (.deb), AppImage, tar.gz
- **macOS**: DMG, ZIP, tar.gz
- **Windows**: MSI, ZIP (planned)

### 3. Commercial Distribution
**Target**: Enterprise customers, paid users
**Components**: Proprietary API daemon, enterprise features
**License**: Commercial EULA

## 🏗️ Build Scripts

### Linux Build (`build_linux.sh`)
```bash
# Full build with all components
./packaging/build_linux.sh

# Build only Python package
./packaging/build_linux.sh package

# Run tests only
./packaging/build_linux.sh test

# Clean build artifacts
./packaging/build_linux.sh clean
```

**Outputs**:
- `dist/sudarshan-engine-1.0.0.tar.gz` - Source distribution
- `dist/sudarshan_engine-1.0.0-py3-none-any.whl` - Universal wheel
- `dist/sudarshan-engine-1.0.0.deb` - Debian package
- `dist/Sudarshan_Engine-1.0.0-x86_64.AppImage` - AppImage

### macOS Build (`build_macos.sh`)
```bash
# Full build with all components
./packaging/build_macos.sh

# Build only Python package
./packaging/build_macos.sh package

# Run tests only
./packaging/build_macos.sh test

# Clean build artifacts
./packaging/build_macos.sh clean
```

**Outputs**:
- `dist/sudarshan-engine-1.0.0.tar.gz` - Source distribution
- `dist/sudarshan_engine-1.0.0-py3-none-any.whl` - Universal wheel
- `dist/Sudarshan_Engine-1.0.0.dmg` - macOS DMG
- `dist/Sudarshan_Engine-1.0.0-macOS.zip` - ZIP archive

### Windows Build (Planned)
```bash
# Future Windows build script
./packaging/build_windows.ps1
```

## 📤 PyPI Upload

### Prerequisites
1. **PyPI Account**: Create account at https://pypi.org/
2. **API Token**: Generate token at https://pypi.org/manage/account/token/
3. **Twine**: Install with `pip install twine`

### Environment Setup
```bash
# Set API tokens (add to ~/.bashrc or ~/.zshrc)
export PYPI_API_TOKEN="your_production_token"
export TEST_PYPI_API_TOKEN="your_test_token"
```

### Upload Process
```bash
# Test upload first (recommended)
python packaging/upload_pypi.py --test

# Check test package at: https://test.pypi.org/project/sudarshan-engine/

# Production upload
python packaging/upload_pypi.py --production

# Or both in one command
python packaging/upload_pypi.py --test --production
```

### Upload Options
```bash
# Skip validation (not recommended)
python packaging/upload_pypi.py --skip-validation --production

# Clean up old files before upload
python packaging/upload_pypi.py --cleanup --production
```

## 📋 Build Dependencies

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    ninja-build \
    libssl-dev \
    python3-dev \
    python3-pip \
    doxygen \
    graphviz \
    valgrind \
    liboqs-dev
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake ninja openssl@3 wget doxygen graphviz astyle valgrind liboqs
```

#### Windows (Planned)
```powershell
# Install dependencies via Chocolatey or manual installation
choco install cmake ninja openssl python3
# Build liboqs from source
```

### Python Dependencies
```bash
# Install build tools
pip install setuptools wheel twine

# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]
```

## 🔧 Build Process

### 1. Prepare Environment
```bash
# Clone repository
git clone https://github.com/sudarshan-engine/sudarshan-engine.git
cd sudarshan-engine

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies
```bash
# Install system dependencies (see above)

# Install Python dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 3. Build liboqs (if not available)
```bash
# Linux/macOS
./packaging/build_linux.sh  # or build_macos.sh

# This will automatically build and install liboqs if needed
```

### 4. Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=sudarshan --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/security/ -v
```

### 5. Build Package
```bash
# Build Python package
python setup.py sdist bdist_wheel

# Build platform-specific packages
./packaging/build_linux.sh package  # Linux
./packaging/build_macos.sh package  # macOS
```

### 6. Upload to PyPI
```bash
# Test upload
python packaging/upload_pypi.py --test

# Production upload (after testing)
python packaging/upload_pypi.py --production
```

## 📦 Package Structure

### Source Distribution
```
sudarshan-engine-1.0.0/
├── sudarshan/              # Main package
│   ├── __init__.py        # Package initialization
│   ├── crypto.py          # Cryptographic operations
│   ├── spq_format.py      # .spq file handling
│   ├── protocols.py       # Box-in-a-Box protocols
│   ├── cli.py            # Command-line interface
│   └── ...
├── docs/                  # Documentation
├── examples/              # Usage examples
├── tests/                 # Test suite
├── packaging/             # Build scripts
├── sudarshan.py           # CLI entry point
├── setup.py              # Package configuration
├── MANIFEST.in           # Package manifest
├── LICENSE               # AGPL-3.0 license
└── README.md             # Project README
```

### Wheel Distribution
```
sudarshan_engine-1.0.0-py3-none-any.whl
├── sudarshan/
│   ├── __init__.py
│   ├── crypto.py
│   ├── spq_format.py
│   └── ...
├── sudarshan-1.0.0.dist-info/
│   ├── METADATA
│   ├── WHEEL
│   └── RECORD
```

## 🚀 Installation Methods

### From PyPI
```bash
# Install latest version
pip install sudarshan-engine

# Install specific version
pip install sudarshan-engine==1.0.0

# Install with extras
pip install sudarshan-engine[gui,web,security]
```

### From Source
```bash
# Clone repository
git clone https://github.com/sudarshan-engine/sudarshan-engine.git
cd sudarshan-engine

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### From Native Packages

#### Linux (Debian/Ubuntu)
```bash
# Install .deb package
sudo dpkg -i sudarshan-engine-1.0.0.deb
sudo apt install -f  # Fix dependencies

# Or use AppImage
chmod +x Sudarshan_Engine-1.0.0-x86_64.AppImage
./Sudarshan_Engine-1.0.0-x86_64.AppImage
```

#### macOS
```bash
# Mount DMG and drag to Applications
open Sudarshan_Engine-1.0.0.dmg

# Or extract ZIP
unzip Sudarshan_Engine-1.0.0-macOS.zip
```

## 🔒 Security Considerations

### Build Security
- **Reproducible Builds**: All builds use pinned dependencies
- **Code Signing**: Release builds are code-signed
- **Supply Chain Security**: Dependencies are verified
- **Vulnerability Scanning**: Automated security scanning in CI/CD

### Distribution Security
- **PyPI Security**: Uploads require API tokens
- **Checksum Verification**: All packages include SHA256 checksums
- **GPG Signing**: Release packages are GPG-signed
- **Secure Channels**: All distribution uses HTTPS/TLS

## 📊 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/build.yml
name: Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .[dev]
      - name: Run tests
        run: python -m pytest tests/ --cov=sudarshan
      - name: Build package
        run: python setup.py sdist bdist_wheel
```

### Automated Releases
```yaml
# .github/workflows/release.yml
name: Release
on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install twine
      - name: Build and publish
        env:
          PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          python setup.py sdist bdist_wheel
          python packaging/upload_pypi.py --production
```

## 🐛 Troubleshooting

### Common Build Issues

#### liboqs Not Found
```bash
# Install liboqs system-wide
sudo apt install liboqs-dev  # Linux
brew install liboqs          # macOS

# Or build from source
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
make && sudo make install
```

#### Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Build Failures
```bash
# Clean and rebuild
./packaging/build_linux.sh clean
./packaging/build_linux.sh

# Check build logs
tail -f build/build.log
```

### Distribution Issues

#### PyPI Upload Fails
```bash
# Check API token
echo $PYPI_API_TOKEN

# Test with test PyPI first
python packaging/upload_pypi.py --test

# Check package metadata
python setup.py check
```

#### Native Package Issues
```bash
# Check package contents
dpkg -c sudarshan-engine-1.0.0.deb

# Verify AppImage
./Sudarshan_Engine-1.0.0-x86_64.AppImage --version
```

## 📞 Support

- **Documentation**: https://docs.sudarshan-engine.org
- **Issues**: https://github.com/sudarshan-engine/sudarshan-engine/issues
- **Discussions**: https://github.com/sudarshan-engine/sudarshan-engine/discussions
- **Security**: security@sudarshanengine.xyz

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for build and packaging guidelines.

---

**🎯 Ready to distribute Sudarshan Engine worldwide! Choose your platform and deployment method above.**