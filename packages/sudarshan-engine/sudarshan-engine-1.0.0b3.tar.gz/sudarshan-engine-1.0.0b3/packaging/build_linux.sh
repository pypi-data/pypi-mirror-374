#!/bin/bash
# Sudarshan Engine Linux Build Script
# Builds and packages Sudarshan Engine for Linux distributions

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sudarshan-engine"
VERSION=$(python -c "import sys; sys.path.insert(0, '.'); exec(open('setup.py').read()); print(__version__)" 2>/dev/null || echo "1.0.0")
BUILD_DIR="build"
DIST_DIR="dist"
PACKAGE_NAME="${PROJECT_NAME}-${VERSION}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed."
        exit 1
    fi

    # Check system dependencies
    local missing_deps=()

    if ! dpkg -l | grep -q liboqs-dev; then
        missing_deps+=("liboqs-dev")
    fi

    if ! dpkg -l | grep -q libssl-dev; then
        missing_deps+=("libssl-dev")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warning "Missing system dependencies: ${missing_deps[*]}"
        log_info "Installing missing dependencies..."
        sudo apt update
        sudo apt install -y "${missing_deps[@]}"
    fi

    log_success "Prerequisites check completed"
}

# Setup build environment
setup_build_env() {
    log_info "Setting up build environment..."

    # Create build directories
    mkdir -p "$BUILD_DIR"
    mkdir -p "$DIST_DIR"

    # Clean previous builds
    rm -rf "$BUILD_DIR"/*
    rm -rf "$DIST_DIR"/*

    # Create virtual environment for build
    python3 -m venv "$BUILD_DIR/venv"
    source "$BUILD_DIR/venv/bin/activate"

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    log_success "Build environment setup completed"
}

# Build liboqs if not available
build_liboqs() {
    log_info "Checking for liboqs..."

    if ! pkg-config --exists liboqs; then
        log_warning "liboqs not found, building from source..."

        # Clone and build liboqs
        git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git "$BUILD_DIR/liboqs"
        cd "$BUILD_DIR/liboqs"

        mkdir build && cd build
        cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
        make -j$(nproc)
        sudo make install

        # Update library cache
        sudo ldconfig

        cd ../../../
        log_success "liboqs built and installed"
    else
        log_info "liboqs already available"
    fi
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."

    source "$BUILD_DIR/venv/bin/activate"

    # Install build dependencies
    pip install -r requirements.txt

    # Install development dependencies
    pip install pytest pytest-cov pytest-xdist twine

    log_success "Python dependencies installed"
}

# Build Python package
build_package() {
    log_info "Building Python package..."

    source "$BUILD_DIR/venv/bin/activate"

    # Build source distribution
    python setup.py sdist

    # Build wheel
    python setup.py bdist_wheel

    log_success "Python package built"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    source "$BUILD_DIR/venv/bin/activate"

    # Run unit tests
    python -m pytest tests/unit/ -v --cov=sudarshan --cov-report=html

    # Run integration tests
    python -m pytest tests/integration/ -v

    log_success "Tests completed"
}

# Create Debian package
create_debian_package() {
    log_info "Creating Debian package..."

    local debian_dir="$BUILD_DIR/debian"
    mkdir -p "$debian_dir"

    # Create Debian package structure
    mkdir -p "$debian_dir/DEBIAN"
    mkdir -p "$debian_dir/usr/bin"
    mkdir -p "$debian_dir/usr/lib/python3/dist-packages"
    mkdir -p "$debian_dir/usr/share/sudarshan"
    mkdir -p "$debian_dir/usr/share/doc/sudarshan"

    # Copy files
    cp -r sudarshan "$debian_dir/usr/lib/python3/dist-packages/"
    cp sudarshan.py "$debian_dir/usr/bin/sudarshan"
    chmod +x "$debian_dir/usr/bin/sudarshan"

    # Copy documentation
    cp README.md LICENSE "$debian_dir/usr/share/doc/sudarshan/"

    # Create control file
    cat > "$debian_dir/DEBIAN/control" << EOF
Package: sudarshan-engine
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pip, liboqs0, libssl-dev
Maintainer: Sudarshan Engine Team <team@sudarshan.engine>
Description: Universal quantum-safe cybersecurity engine
 Sudarshan Engine is a comprehensive quantum-safe cybersecurity platform
 that provides end-to-end protection for digital assets using
 post-quantum cryptography (PQC) algorithms.
 .
 Features:
  * Quantum-safe encryption with NIST-approved PQC algorithms
  * Multi-layered security with Box-in-a-Box architecture
  * Hardware security module integration
  * Comprehensive audit logging and monitoring
  * Open-core model with commercial extensions
EOF

    # Create postinst script
    cat > "$debian_dir/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Create default directories
mkdir -p /usr/local/share/sudarshan
chmod 755 /usr/local/share/sudarshan

# Update Python path
python3 -m compileall /usr/lib/python3/dist-packages/sudarshan/

echo "Sudarshan Engine installed successfully!"
echo "Run 'sudarshan --help' to get started."
EOF

    chmod +x "$debian_dir/DEBIAN/postinst"

    # Build Debian package
    dpkg-deb --build "$debian_dir" "$DIST_DIR/${PACKAGE_NAME}.deb"

    log_success "Debian package created: $DIST_DIR/${PACKAGE_NAME}.deb"
}

# Create AppImage
create_appimage() {
    log_info "Creating AppImage..."

    local appimage_dir="$BUILD_DIR/AppImage"
    mkdir -p "$appimage_dir"

    # Create AppDir structure
    mkdir -p "$appimage_dir/AppDir/usr/bin"
    mkdir -p "$appimage_dir/AppDir/usr/lib"
    mkdir -p "$appimage_dir/AppDir/usr/share/sudarshan"

    # Copy application files
    cp sudarshan.py "$appimage_dir/AppDir/usr/bin/sudarshan"
    cp -r sudarshan "$appimage_dir/AppDir/usr/lib/"
    cp -r examples "$appimage_dir/AppDir/usr/share/sudarshan/"
    cp -r docs "$appimage_dir/AppDir/usr/share/sudarshan/"

    # Create desktop file
    cat > "$appimage_dir/AppDir/sudarshan.desktop" << EOF
[Desktop Entry]
Name=Sudarshan Engine
Exec=sudarshan
Icon=sudarshan
Type=Application
Categories=Utility;Security;
EOF

    # Create AppRun script
    cat > "$appimage_dir/AppDir/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/lib:${PYTHONPATH}"
exec "${HERE}/usr/bin/sudarshan" "$@"
EOF

    chmod +x "$appimage_dir/AppDir/AppRun"

    # Download and use appimagetool if available
    if command -v appimagetool &> /dev/null; then
        appimagetool "$appimage_dir/AppDir" "$DIST_DIR/Sudarshan_Engine-${VERSION}-x86_64.AppImage"
        log_success "AppImage created: $DIST_DIR/Sudarshan_Engine-${VERSION}-x86_64.AppImage"
    else
        log_warning "appimagetool not found, skipping AppImage creation"
        log_info "To create AppImage, install appimagetool:"
        log_info "wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        log_info "chmod +x appimagetool-x86_64.AppImage"
    fi
}

# Create distribution archives
create_archives() {
    log_info "Creating distribution archives..."

    # Create tar.gz archive
    tar -czf "$DIST_DIR/${PACKAGE_NAME}.tar.gz" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='build' \
        --exclude='dist' \
        --exclude='.pytest_cache' \
        --exclude='htmlcov' \
        --exclude='*.egg-info' \
        .

    log_success "Tar.gz archive created: $DIST_DIR/${PACKAGE_NAME}.tar.gz"
}

# Main build function
main() {
    log_info "Starting Sudarshan Engine Linux build..."
    log_info "Version: $VERSION"
    log_info "Package: $PACKAGE_NAME"

    check_prerequisites
    setup_build_env
    build_liboqs
    install_dependencies
    build_package
    run_tests
    create_debian_package
    create_appimage
    create_archives

    log_success "Build completed successfully!"
    log_info "Distribution files created in: $DIST_DIR"
    ls -la "$DIST_DIR"

    log_info "Installation instructions:"
    echo "  # Install Debian package:"
    echo "  sudo dpkg -i $DIST_DIR/${PACKAGE_NAME}.deb"
    echo "  sudo apt install -f  # Fix dependencies if needed"
    echo ""
    echo "  # Or install from source:"
    echo "  pip install $DIST_DIR/${PACKAGE_NAME}.tar.gz"
    echo ""
    echo "  # Run the application:"
    echo "  sudarshan --help"
}

# Handle command line arguments
case "${1:-}" in
    "clean")
        log_info "Cleaning build artifacts..."
        rm -rf "$BUILD_DIR" "$DIST_DIR" *.egg-info
        log_success "Clean completed"
        ;;
    "test")
        setup_build_env
        install_dependencies
        run_tests
        ;;
    "package")
        setup_build_env
        install_dependencies
        build_package
        ;;
    *)
        main
        ;;
esac