#!/bin/bash
# Sudarshan Engine macOS Build Script
# Builds and packages Sudarshan Engine for macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sudarshan-engine"
VERSION=$(python3 -c "import sys; sys.path.insert(0, '.'); exec(open('setup.py').read()); print(__version__)" 2>/dev/null || echo "1.0.0")
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

    # Check Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        log_error "Xcode Command Line Tools are required."
        log_info "Install with: xcode-select --install"
        exit 1
    fi

    # Check Homebrew
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew is required."
        log_info "Install from: https://brew.sh/"
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required."
        exit 1
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

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."

    # Install build dependencies
    brew install cmake ninja openssl@3 wget doxygen graphviz astyle valgrind

    # Install Python dependencies
    pip install pytest pytest-cov pytest-xdist pyyaml

    log_success "System dependencies installed"
}

# Build liboqs
build_liboqs() {
    log_info "Building liboqs..."

    # Clone liboqs
    git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git "$BUILD_DIR/liboqs"
    cd "$BUILD_DIR/liboqs"

    # Build with cmake
    mkdir build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=/usr/local ..
    make -j$(sysctl -n hw.ncpu)
    sudo make install

    # Update library cache
    sudo update_dyld_shared_cache

    cd ../../../
    log_success "liboqs built and installed"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."

    source "$BUILD_DIR/venv/bin/activate"

    # Install from requirements.txt
    pip install -r requirements.txt

    # Install development dependencies
    pip install twine

    log_success "Python dependencies installed"
}

# Build Python package
build_package() {
    log_info "Building Python package..."

    source "$BUILD_DIR/venv/bin/activate"

    # Build universal wheel for macOS
    python setup.py sdist
    python setup.py bdist_wheel --universal

    log_success "Python package built"
}

# Create macOS application bundle
create_app_bundle() {
    log_info "Creating macOS application bundle..."

    local bundle_dir="$BUILD_DIR/Sudarshan Engine.app"
    local contents_dir="$bundle_dir/Contents"
    local macos_dir="$contents_dir/MacOS"
    local resources_dir="$contents_dir/Resources"

    # Create bundle structure
    mkdir -p "$macos_dir"
    mkdir -p "$resources_dir"

    # Create Info.plist
    cat > "$contents_dir/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>sudarshan</string>
    <key>CFBundleIdentifier</key>
    <string>org.sudarshan.engine</string>
    <key>CFBundleName</key>
    <string>Sudarshan Engine</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
EOF

    # Create executable script
    cat > "$macos_dir/sudarshan" << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="$DIR/../Resources/lib/python3.9/site-packages" "$DIR/../Resources/bin/python3" -m sudarshan "$@"
EOF

    chmod +x "$macos_dir/sudarshan"

    # Copy Python environment
    source "$BUILD_DIR/venv/bin/activate"
    cp -r "$BUILD_DIR/venv" "$resources_dir/python"

    # Copy application files
    cp -r sudarshan "$resources_dir/lib/python3.9/site-packages/"
    cp sudarshan.py "$macos_dir/"

    # Create DMG
    if command -v create-dmg &> /dev/null; then
        create-dmg \
            --volname "Sudarshan Engine $VERSION" \
            --volicon "icon.icns" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --icon "Sudarshan Engine.app" 200 190 \
            --hide-extension "Sudarshan Engine.app" \
            --app-drop-link 600 185 \
            "$DIST_DIR/Sudarshan_Engine-${VERSION}.dmg" \
            "$bundle_dir"
        log_success "DMG created: $DIST_DIR/Sudarshan_Engine-${VERSION}.dmg"
    else
        log_warning "create-dmg not found, creating ZIP instead"
        cd "$BUILD_DIR"
        zip -r "$DIST_DIR/Sudarshan_Engine-${VERSION}-macOS.zip" "Sudarshan Engine.app"
        cd ..
        log_success "ZIP created: $DIST_DIR/Sudarshan_Engine-${VERSION}-macOS.zip"
    fi
}

# Create distribution archives
create_archives() {
    log_info "Creating distribution archives..."

    # Create tar.gz archive
    tar -czf "$DIST_DIR/${PACKAGE_NAME}-macOS.tar.gz" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='build' \
        --exclude='dist' \
        --exclude='.pytest_cache' \
        --exclude='htmlcov' \
        --exclude='*.egg-info' \
        .

    log_success "Tar.gz archive created: $DIST_DIR/${PACKAGE_NAME}-macOS.tar.gz"
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

# Main build function
main() {
    log_info "Starting Sudarshan Engine macOS build..."
    log_info "Version: $VERSION"
    log_info "Package: $PACKAGE_NAME"

    check_prerequisites
    setup_build_env
    install_system_deps
    build_liboqs
    install_dependencies
    build_package
    run_tests
    create_app_bundle
    create_archives

    log_success "macOS build completed successfully!"
    log_info "Distribution files created in: $DIST_DIR"
    ls -la "$DIST_DIR"

    log_info "Installation instructions:"
    echo "  # Install from DMG:"
    echo "  Open $DIST_DIR/Sudarshan_Engine-${VERSION}.dmg and drag to Applications"
    echo ""
    echo "  # Or install from source:"
    echo "  pip install $DIST_DIR/${PACKAGE_NAME}.tar.gz"
    echo ""
    echo "  # Run the application:"
    echo "  /Applications/Sudarshan\\ Engine.app/Contents/MacOS/sudarshan --help"
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