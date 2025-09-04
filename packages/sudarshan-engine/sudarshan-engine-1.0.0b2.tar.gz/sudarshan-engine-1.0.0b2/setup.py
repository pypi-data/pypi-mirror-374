#!/usr/bin/env python3
"""
Setup script for Sudarshan Engine.

This script handles the installation and distribution of Sudarshan Engine.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Add the sudarshan package to the path for importing version info
sys.path.insert(0, str(Path(__file__).parent / "sudarshan"))

try:
    from __version__ import (
        __version__,
        __version_info__,
        IS_BETA,
        BETA_VERSION,
        GITHUB_REPO,
        get_release_info
    )
except ImportError:
    # Fallback if version module is not available
    __version__ = "1.0.0-beta.1"
    __version_info__ = (1, 0, 0, "beta", 1)
    IS_BETA = True
    BETA_VERSION = 1
    GITHUB_REPO = "https://github.com/Yash-Sharma1810/sudarshan-engine"

# Read README for long description
def read_readme():
    """Read README file for long description."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    requirements_path = Path(__file__).parent / filename
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Package metadata
PACKAGE_NAME = "sudarshan-engine"
PACKAGE_VERSION = __version__
PACKAGE_AUTHOR = "Yash Sharma"
PACKAGE_AUTHOR_EMAIL = "yash02.prof@gmail.com"
PACKAGE_DESCRIPTION = "Universal Quantum-Safe Cybersecurity Engine"
PACKAGE_URL = GITHUB_REPO
PACKAGE_LICENSE = "AGPL-3.0"

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta" if IS_BETA else "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Security :: Cryptography",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Archiving :: Compression",
]

# Keywords for PyPI
KEYWORDS = [
    "quantum-safe",
    "cryptography",
    "post-quantum",
    "pqc",
    "encryption",
    "security",
    "kyber",
    "dilithium",
    "falcon",
    "blockchain",
    "wallet",
    "cybersecurity"
]

# Dependencies
INSTALL_REQUIRES = [
    "cryptography>=3.4.0",
    "pycryptodome>=3.10.0",
    "click>=8.0.0",
    "pyyaml>=5.4.0",
    "requests>=2.25.0",
    "tqdm>=4.60.0",
]

# Optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
        "pytest-xdist>=2.5.0",
        "flake8>=3.9.0",
        "black>=21.0.0",
        "mypy>=0.800",
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "bandit>=1.7.0",
        "safety>=1.10.0",
    ],
    "gui": [
        "PyQt5>=5.15.0",
        "PyQtWebEngine>=5.15.0",
    ],
    "web": [
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "werkzeug>=2.0.0",
    ],
    "enterprise": [
        "psycopg2-binary>=2.9.0",
        "pymongo>=3.12.0",
        "redis>=3.5.0",
        "celery>=5.2.0",
    ],
    "all": [
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
        "pytest-xdist>=2.5.0",
        "flake8>=3.9.0",
        "black>=21.0.0",
        "mypy>=0.800",
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "bandit>=1.7.0",
        "safety>=1.10.0",
        "PyQt5>=5.15.0",
        "PyQtWebEngine>=5.15.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "werkzeug>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pymongo>=3.12.0",
        "redis>=3.5.0",
        "celery>=5.2.0",
    ]
}

# Entry points for console scripts
ENTRY_POINTS = {
    "console_scripts": [
        "sudarshan=sudarshan.cli:main",
        "sudarshan-cli=sudarshan.cli:main",
        "sudarshan-engine=sudarshan.cli:main",
    ],
}

# Package data
PACKAGE_DATA = {
    "sudarshan": [
        "data/*",
        "templates/*",
        "static/*",
        "migrations/*",
    ],
}

# Include package data
INCLUDE_PACKAGE_DATA = True

# Setup configuration
setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    description=PACKAGE_DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url=PACKAGE_URL,
    license=PACKAGE_LICENSE,

    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*", "scripts*"]),
    include_package_data=INCLUDE_PACKAGE_DATA,
    package_data=PACKAGE_DATA,
    license_files=[],  # Disable automatic license file inclusion

    # Dependencies
    python_requires=">=3.8.0",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,

    # Entry points
    entry_points=ENTRY_POINTS,

    # Metadata
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,

    # Project links
    project_urls={
        "Bug Reports": f"{GITHUB_REPO}/issues",
        "Source": GITHUB_REPO,
        "Documentation": "https://sudarshan-engine.readthedocs.io/",
        "Changelog": f"{GITHUB_REPO}/blob/main/CHANGELOG.md",
        "Funding": "https://github.com/sponsors/Yash-Sharma1810",
    },

    # Additional metadata
    zip_safe=False,
    platforms=["any"],
)

# Post-installation message
def print_post_install_message():
    """Print post-installation message."""
    beta_msg = ""
    if IS_BETA:
        beta_msg = f"""

⚠️  BETA VERSION NOTICE:
   This is beta version {BETA_VERSION} of Sudarshan Engine.
   Some features may be unstable or subject to change.
   Please report any issues to: {GITHUB_REPO}/issues

   For production use, wait for the stable v1.0.0 release.
"""

    message = f"""
🎉 Sudarshan Engine {PACKAGE_VERSION} installed successfully!

📚 Documentation: https://sudarshan-engine.readthedocs.io/
🐛 Report Issues: {GITHUB_REPO}/issues
💬 Community: {GITHUB_REPO}/discussions

🚀 Quick Start:
   sudarshan --help
   sudarshan spq_create --input myfile.txt --output myfile.spq

🔐 Security Notice:
   - Keep your encryption passwords secure
   - Use strong, unique passwords
   - Regularly backup your encrypted files
   - Report security issues to: security@sudarshanengine.xyz{beta_msg}

Thank you for choosing Sudarshan Engine! 🛡️✨
"""

    print(message)

# Print the message after setup
if __name__ == "__main__":
    print_post_install_message()