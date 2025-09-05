Installation Guide
==================

This guide covers installing Sudarshan Engine on various platforms and environments.

.. contents::
   :local:
   :depth: 2

System Requirements
===================

**Minimum Requirements:**

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 512 MB
- **Disk Space**: 100 MB
- **Network**: Internet connection for installation

**Recommended Requirements:**

- **Operating System**: Linux (Ubuntu 20.04+) or macOS (10.15+)
- **Python**: 3.9 or higher
- **RAM**: 1 GB
- **Disk Space**: 500 MB
- **Hardware Security**: TPM/HSM/SGX (optional but recommended)

Prerequisites
=============

Linux (Ubuntu/Debian)
---------------------

Install system dependencies:

.. code-block:: bash

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
       pkg-config

macOS
-----

Install Xcode Command Line Tools:

.. code-block:: bash

   xcode-select --install

Install Homebrew (if not already installed):

.. code-block:: bash

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install dependencies:

.. code-block:: bash

   brew install cmake ninja openssl@3 wget doxygen graphviz astyle valgrind pkg-config

Windows
-------

**Option 1: Chocolatey (Recommended)**

.. code-block:: powershell

   # Install Chocolatey
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

   # Install dependencies
   choco install cmake ninja python3 openssl git

**Option 2: Manual Installation**

Download and install:

1. `Python 3.8+ <https://python.org/downloads/>`_
2. `CMake <https://cmake.org/download/>`_
3. `Ninja <https://github.com/ninja-build/ninja/releases>`_
4. `OpenSSL <https://slproweb.com/products/Win32OpenSSL.html>`_
5. `Git <https://git-scm.com/download/win>`_

Installation Methods
===================

Method 1: PyPI (Recommended)
-----------------------------

**Stable Release:**

.. code-block:: bash

   pip install sudarshan-engine

**Development Version:**

.. code-block:: bash

   pip install --pre sudarshan-engine

**With Optional Dependencies:**

.. code-block:: bash

   # Full installation with GUI and web interface
   pip install sudarshan-engine[gui,web,security]

   # Minimal installation (CLI only)
   pip install sudarshan-engine

Method 2: From Source
---------------------

**Git Clone:**

.. code-block:: bash

   git clone https://github.com/sudarshan-engine/sudarshan-engine.git
   cd sudarshan-engine

**Install in Development Mode:**

.. code-block:: bash

   # Install with all dependencies
   pip install -e .[dev,gui,web,security]

   # Install minimal version
   pip install -e .

**Build from Source (Advanced):**

.. code-block:: bash

   # Install Python dependencies
   pip install -r requirements.txt

   # Build liboqs (quantum-safe crypto library)
   ./packaging/build_linux.sh  # Linux
   ./packaging/build_macos.sh  # macOS

   # Install
   python setup.py develop

Method 3: Docker
----------------

**Official Docker Image:**

.. code-block:: bash

   # Pull the latest image
   docker pull sudarshan/engine:latest

   # Run container
   docker run -it sudarshan/engine:latest

**Build from Dockerfile:**

.. code-block:: bash

   # Clone repository
   git clone https://github.com/sudarshan-engine/sudarshan-engine.git
   cd sudarshan-engine

   # Build Docker image
   docker build -t sudarshan-engine .

   # Run container
   docker run -it sudarshan-engine

Method 4: Native Packages
-------------------------

**Linux (Debian/Ubuntu):**

.. code-block:: bash

   # Download .deb package
   wget https://github.com/sudarshan-engine/sudarshan-engine/releases/download/v1.0.0/sudarshan-engine-1.0.0.deb

   # Install
   sudo dpkg -i sudarshan-engine-1.0.0.deb
   sudo apt install -f  # Fix dependencies

**Linux (AppImage):**

.. code-block:: bash

   # Download AppImage
   wget https://github.com/sudarshan-engine/sudarshan-engine/releases/download/v1.0.0/Sudarshan_Engine-1.0.0-x86_64.AppImage

   # Make executable and run
   chmod +x Sudarshan_Engine-1.0.0-x86_64.AppImage
   ./Sudarshan_Engine-1.0.0-x86_64.AppImage

**macOS:**

.. code-block:: bash

   # Download DMG
   curl -L -o Sudarshan_Engine-1.0.0.dmg https://github.com/sudarshan-engine/sudarshan-engine/releases/download/v1.0.0/Sudarshan_Engine-1.0.0.dmg

   # Mount and install
   hdiutil attach Sudarshan_Engine-1.0.0.dmg
   cp -r /Volumes/Sudarshan\ Engine/Sudarshan\ Engine.app /Applications/

Method 5: Conda/Mamba
---------------------

**Conda Installation:**

.. code-block:: bash

   # Install conda (if not already installed)
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh

   # Create environment
   conda create -n sudarshan python=3.9
   conda activate sudarshan

   # Install
   conda install -c conda-forge sudarshan-engine

**Mamba Installation:**

.. code-block:: bash

   # Install mamba
   conda install -c conda-forge mamba

   # Create environment and install
   mamba create -n sudarshan python=3.9 sudarshan-engine
   mamba activate sudarshan

Verification
===========

**Check Installation:**

.. code-block:: bash

   # Check Python package
   python -c "import sudarshan; print(f'Sudarshan Engine {sudarshan.__version__}')"

   # Check CLI
   sudarshan --version

   # Check crypto libraries
   python -c "from sudarshan.crypto import QuantumSafeCrypto; print('✅ Crypto module loaded')"

**Run Basic Test:**

.. code-block:: bash

   # Create test file
   echo "Hello, Quantum World!" > test.txt

   # Encrypt with Sudarshan
   sudarshan spq_create --input test.txt --output test.spq --password test123

   # Verify file was created
   ls -la test.spq

   # Decrypt and verify
   sudarshan spq_read --input test.spq --password test123

   # Clean up
   rm test.txt test.spq

Configuration
=============

**Environment Variables:**

.. code-block:: bash

   # Set custom data directory
   export SUDARSHAN_DATA_DIR=/path/to/data

   # Set log level
   export SUDARSHAN_LOG_LEVEL=INFO

   # Set crypto backend
   export SUDARSHAN_CRYPTO_BACKEND=liboqs

   # Set security level
   export SUDARSHAN_SECURITY_LEVEL=high

**Configuration File:**

Create ``~/.sudarshan/config.yaml``:

.. code-block:: yaml

   # Sudarshan Engine Configuration
   data_directory: ~/.sudarshan/data
   log_level: INFO
   crypto_backend: liboqs
   security_level: high

   # Algorithm preferences
   default_kem: kyber1024
   default_signature: dilithium5
   default_symmetric: aes256

   # Hardware security
   enable_hsm: true
   enable_tpm: true
   enable_sgx: true

   # Network settings
   api_timeout: 30
   max_connections: 100

Troubleshooting
===============

**Common Issues:**

**1. Import Error:**

.. code-block:: bash

   # Error: ModuleNotFoundError: No module named 'sudarshan'
   pip install sudarshan-engine

**2. Crypto Library Error:**

.. code-block:: bash

   # Error: liboqs not found
   # On Linux
   sudo apt install liboqs-dev

   # On macOS
   brew install liboqs

   # Or build from source
   git clone https://github.com/open-quantum-safe/liboqs.git
   cd liboqs && mkdir build && cd build
   cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
   make && sudo make install

**3. Permission Error:**

.. code-block:: bash

   # Error: Permission denied
   sudo chown -R $USER:$USER ~/.sudarshan
   chmod 700 ~/.sudarshan

**4. Memory Error:**

.. code-block:: bash

   # Error: Out of memory
   # Increase swap space or use smaller files
   # For large files, use streaming mode
   sudarshan spq_create --input large_file.dat --output large_file.spq --stream

**5. Network Error:**

.. code-block:: bash

   # Error: Connection timeout
   # Check network connectivity
   ping github.com

   # Use local installation
   pip install --no-index --find-links=/path/to/wheels sudarshan-engine

**6. GUI Not Starting:**

.. code-block:: bash

   # Error: GUI application not found
   # Install GUI dependencies
   pip install sudarshan-engine[gui]

   # On Linux, install system GUI libraries
   sudo apt install libgtk-3-dev libwebkit2gtk-4.0-dev

**7. Web Interface Not Accessible:**

.. code-block:: bash

   # Error: Web server not starting
   # Check port availability
   netstat -tlnp | grep :8080

   # Start on different port
   sudarshan web --port 8081

Uninstallation
==============

**PyPI Installation:**

.. code-block:: bash

   pip uninstall sudarshan-engine

**From Source:**

.. code-block:: bash

   # Remove development installation
   pip uninstall sudarshan-engine
   rm -rf sudarshan_engine.egg-info

**Native Packages:**

.. code-block:: bash

   # Debian/Ubuntu
   sudo apt remove sudarshan-engine

   # macOS
   rm -rf /Applications/Sudarshan\ Engine.app

**Docker:**

.. code-block:: bash

   # Stop and remove containers
   docker stop sudarshan-container
   docker rm sudarshan-container

   # Remove image
   docker rmi sudarshan/engine

**Complete Cleanup:**

.. code-block:: bash

   # Remove configuration and data
   rm -rf ~/.sudarshan

   # Remove logs
   rm -rf /var/log/sudarshan

   # Remove temporary files
   rm -rf /tmp/sudarshan*

Next Steps
==========

Now that Sudarshan Engine is installed, you can:

1. **Read the Quick Start Guide**: :doc:`quickstart`
2. **Explore the CLI**: :doc:`guides/cli_usage`
3. **Try the Desktop App**: :doc:`guides/desktop_app`
4. **Check out Examples**: :doc:`examples/basic_usage`

For support and questions:

- **Documentation**: https://docs.sudarshan.engine
- **GitHub Issues**: https://github.com/sudarshan-engine/sudarshan-engine/issues
- **Community Forum**: https://community.sudarshan.engine

.. note::
   Sudarshan Engine requires an internet connection for initial setup and license verification. Once configured, it can operate offline.

.. tip::
   For production deployments, consider using the Docker installation method for better isolation and easier updates.