"""
Version information for Sudarshan Engine.

This module provides version information and compatibility checking for the Sudarshan Engine.
"""

import re
from typing import Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

__version__ = "1.0.0-beta.2"
__version_info__ = (1, 0, 0, "beta", 2)

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_SUFFIX = "beta.2"  # e.g., "dev", "rc1", "beta.1"

# Release information
IS_BETA = True
BETA_VERSION = 2
RELEASE_DATE = "2025-09-02"
GITHUB_REPO = "https://github.com/Yash-Sharma1810/sudarshan_engine"
DOCUMENTATION_URL = "https://github.com/Yash-Sharma1810/sudarshan_engine"

# File format versions
SPQ_FORMAT_VERSION = "1.0"
SPQ_FORMAT_COMPATIBILITY = ["1.0"]

# API versions
API_VERSION = "v1"
API_COMPATIBILITY = ["v1"]

# Supported quantum-safe algorithms
SUPPORTED_ALGORITHMS = [
    "kyber512",
    "kyber768",
    "kyber1024",
    "dilithium2",
    "dilithium3",
    "dilithium5",
    "falcon512",
    "falcon1024"
]

# Minimum required versions
MIN_PYTHON_VERSION = (3, 8, 0)
MIN_LIBOQS_VERSION = "0.8.0"

def get_version() -> str:
    """Get the current version string."""
    return __version__

def get_version_info() -> Tuple[int, int, int, str, int]:
    """Get the version as a tuple."""
    return __version_info__

def parse_version(version_string: str) -> Tuple[int, int, int, str]:
    """
    Parse a version string into components.

    Args:
        version_string: Version string like "1.2.3" or "1.2.3-beta.1"

    Returns:
        Tuple of (major, minor, patch, suffix)
    """
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?$'
    match = re.match(pattern, version_string)

    if not match:
        raise ValueError(f"Invalid version format: {version_string}")

    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix or ""

def is_compatible_version(required_version: str, current_version: str = None) -> bool:
    """
    Check if current version is compatible with required version.

    Args:
        required_version: Minimum required version
        current_version: Version to check (defaults to current)

    Returns:
        True if compatible, False otherwise
    """
    if current_version is None:
        current_version = __version__

    req_major, req_minor, req_patch, _ = parse_version(required_version)
    cur_major, cur_minor, cur_patch, _ = parse_version(current_version)

    # Major version must match
    if cur_major != req_major:
        return False

    # Minor version must be >= required
    if cur_minor < req_minor:
        return False

    # Patch version must be >= required (for same minor)
    if cur_minor == req_minor and cur_patch < req_patch:
        return False

    return True

def check_spq_compatibility(spq_version: str) -> bool:
    """
    Check if SPQ file format version is compatible.

    Args:
        spq_version: SPQ format version from file

    Returns:
        True if compatible, False otherwise
    """
    return spq_version in SPQ_FORMAT_COMPATIBILITY

def get_upgrade_path(from_version: str, to_version: str) -> Optional[list]:
    """
    Get the upgrade path between versions.

    Args:
        from_version: Starting version
        to_version: Target version

    Returns:
        List of upgrade steps, or None if direct upgrade not possible
    """
    from_major, from_minor, _, _ = parse_version(from_version)
    to_major, to_minor, _, _ = parse_version(to_version)

    # Major version upgrades require special handling
    if to_major > from_major:
        return ["backup_data", "major_upgrade", "migrate_data", "verify_upgrade"]

    # Minor version upgrades are usually safe
    if to_minor > from_minor:
        return ["backup_data", "minor_upgrade", "verify_upgrade"]

    # Same or patch version - no upgrade needed
    return []

def get_deprecation_warnings() -> list:
    """
    Get list of deprecation warnings for current version.

    Returns:
        List of deprecation warning messages
    """
    warnings = []

    # Add warnings for deprecated features
    warnings.append("AES-256-GCM will be deprecated in v1.0 stable, use ChaCha20-Poly1305")
    warnings.append("Beta version: Some APIs may change before stable release")

    return warnings

def get_security_advisories() -> list:
    """
    Get list of security advisories for current version.

    Returns:
        List of security advisory messages
    """
    advisories = []

    # Add security advisories
    advisories.append("Update to latest version for improved quantum resistance")
    advisories.append("Beta version: Report any security issues to security@sudarshanengine.xyz")

    return advisories

def get_beta_features() -> list:
    """
    Get list of beta features in current version.

    Returns:
        List of beta feature descriptions
    """
    features = [
        "Complete quantum-safe encryption engine",
        "Box-in-a-Box security architecture",
        ".spq file format with PQC protection",
        "Multi-platform GUI applications",
        "Enterprise API daemon",
        "Comprehensive testing framework"
    ]

    return features

def get_stability_status() -> str:
    """
    Get the stability status of current version.

    Returns:
        Stability status string
    """
    if IS_BETA:
        return f"Beta {BETA_VERSION} - Not recommended for production use"
    else:
        return "Stable - Production ready"

# Version checking utilities
def require_version(min_version: str, feature: str = "") -> None:
    """
    Require a minimum version for a feature.

    Args:
        min_version: Minimum required version
        feature: Feature name (for error message)

    Raises:
        RuntimeError: If version requirement not met
    """
    if not is_compatible_version(min_version):
        feature_msg = f" for {feature}" if feature else ""
        raise RuntimeError(
            f"Version {min_version} required{feature_msg}, "
            f"but running {__version__}"
        )

def check_system_compatibility() -> dict:
    """
    Check system compatibility with current version.

    Returns:
        Dictionary with compatibility status
    """
    import sys
    import platform

    result = {
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "compatible": True,
        "warnings": [],
        "errors": []
    }

    # Check Python version
    python_version = sys.version_info[:3]
    if python_version < MIN_PYTHON_VERSION:
        result["compatible"] = False
        result["errors"].append(
            f"Python {'.'.join(map(str, MIN_PYTHON_VERSION))}+ required, "
            f"found {'.'.join(map(str, python_version))}"
        )

    # Check platform
    system = platform.system().lower()
    if system not in ["linux", "darwin", "windows"]:
        result["warnings"].append(f"Untested platform: {system}")

    # Add beta warnings
    if IS_BETA:
        result["warnings"].append("Beta version: Some features may be unstable")

    return result

def get_release_info() -> dict:
    """
    Get comprehensive release information.

    Returns:
        Dictionary with release details
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "is_beta": IS_BETA,
        "beta_version": BETA_VERSION,
        "release_date": RELEASE_DATE,
        "stability_status": get_stability_status(),
        "github_repo": GITHUB_REPO,
        "documentation_url": DOCUMENTATION_URL,
        "supported_algorithms": SUPPORTED_ALGORITHMS,
        "deprecation_warnings": get_deprecation_warnings(),
        "security_advisories": get_security_advisories(),
        "beta_features": get_beta_features() if IS_BETA else []
    }

# Export version information
__all__ = [
    "__version__",
    "__version_info__",
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    "VERSION_SUFFIX",
    "IS_BETA",
    "BETA_VERSION",
    "RELEASE_DATE",
    "GITHUB_REPO",
    "DOCUMENTATION_URL",
    "SPQ_FORMAT_VERSION",
    "SPQ_FORMAT_COMPATIBILITY",
    "API_VERSION",
    "API_COMPATIBILITY",
    "SUPPORTED_ALGORITHMS",
    "MIN_PYTHON_VERSION",
    "MIN_LIBOQS_VERSION",
    "get_version",
    "get_version_info",
    "parse_version",
    "is_compatible_version",
    "check_spq_compatibility",
    "get_upgrade_path",
    "get_deprecation_warnings",
    "get_security_advisories",
    "get_beta_features",
    "get_stability_status",
    "require_version",
    "check_system_compatibility",
    "get_release_info"
]