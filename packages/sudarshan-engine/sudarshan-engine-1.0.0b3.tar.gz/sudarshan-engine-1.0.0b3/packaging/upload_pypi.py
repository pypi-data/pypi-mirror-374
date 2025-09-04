#!/usr/bin/env python3
"""
Sudarshan Engine PyPI Upload Script

Uploads the Sudarshan Engine package to PyPI with proper authentication
and error handling.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command with proper error handling."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        sys.exit(1)

def check_prerequisites():
    """Check if all prerequisites for PyPI upload are met."""
    print("🔍 Checking prerequisites...")

    # Check if twine is installed
    try:
        import twine
        print(f"✅ Twine version: {twine.__version__}")
    except ImportError:
        print("❌ Twine not installed. Install with: pip install twine")
        sys.exit(1)

    # Check if dist directory exists
    dist_dir = Path("../dist")
    if not dist_dir.exists():
        print("❌ dist directory not found. Run build first:")
        print("  python setup.py sdist bdist_wheel")
        sys.exit(1)

    # Check for distribution files
    dist_files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
    if not dist_files:
        print("❌ No distribution files found in dist/")
        print("Run: python setup.py sdist bdist_wheel")
        sys.exit(1)

    print(f"✅ Found {len(dist_files)} distribution files:")
    for f in dist_files:
        print(f"  - {f.name}")

    return dist_files

def validate_package():
    """Validate the package before upload."""
    print("🔍 Validating package...")

    # Check setup.py
    setup_py = Path("../setup.py")
    if not setup_py.exists():
        print("❌ setup.py not found")
        sys.exit(1)

    # Validate package metadata
    try:
        result = run_command("python3 ../setup.py check", capture_output=True)
        print("✅ Package metadata validation passed")
    except:
        print("❌ Package metadata validation failed")
        sys.exit(1)

    # Check for required files
    required_files = [
        "README.md",
        "LICENSE",
        "setup.py",
        "sudarshan/__init__.py"
    ]

    for file in required_files:
        if not Path(f"../{file}").exists():
            print(f"❌ Required file missing: {file}")
            sys.exit(1)

    print("✅ Package validation completed")

def test_upload(repository="testpypi"):
    """Test upload to Test PyPI."""
    print(f"🧪 Testing upload to {repository}...")

    # Check for API token
    token_var = "TEST_PYPI_API_TOKEN" if repository == "testpypi" else "PYPI_API_TOKEN"
    api_token = os.environ.get(token_var)

    if not api_token:
        print(f"❌ {token_var} environment variable not set")
        print(f"Get token from: https://{'test.' if repository == 'testpypi' else ''}pypi.org/manage/account/token/")
        return False

    # Test upload
    try:
        cmd = f"/home/yash_sharma/.local/bin/twine upload --repository {repository} --username __token__ --password {api_token} dist/*"
        run_command(cmd, cwd="..")
        print(f"✅ Test upload to {repository} successful!")
        return True
    except:
        print(f"❌ Test upload to {repository} failed")
        return False

def production_upload(skip_confirmation=False):
    """Upload to production PyPI."""
    print("🚀 Uploading to production PyPI...")

    # Check for API token
    api_token = os.environ.get("PYPI_API_TOKEN")
    if not api_token:
        print("❌ PYPI_API_TOKEN environment variable not set")
        print("Get token from: https://pypi.org/manage/account/token/")
        sys.exit(1)

    # Confirm upload
    if not skip_confirmation:
        print("⚠️  This will upload to PRODUCTION PyPI!")
        response = input("Are you sure? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("Upload cancelled")
            return

    # Production upload
    try:
        cmd = f"/home/yash_sharma/.local/bin/twine upload --username __token__ --password {api_token} dist/*"
        run_command(cmd, cwd="..")
        print("✅ Production upload successful!")

        # Log successful upload
        log_upload()

    except Exception as e:
        print(f"❌ Production upload failed: {e}")
        sys.exit(1)

def log_upload():
    """Log successful upload."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "pypi_upload",
        "status": "success",
        "version": get_package_version(),
        "uploader": os.environ.get("USER", "unknown")
    }

    log_file = Path("../packaging/upload_log.jsonl")
    with open(log_file, 'a') as f:
        json.dump(log_entry, f)
        f.write('\n')

def get_package_version():
    """Get package version from setup.py."""
    try:
        with open("../setup.py", 'r') as f:
            content = f.read()

        # Extract version (simple regex)
        import re
        version_match = re.search(r"VERSION\s*=\s*['\"]([^'\"]*)['\"]", content)
        if version_match:
            return version_match.group(1)
    except:
        pass
    return "unknown"

def cleanup_old_files():
    """Clean up old distribution files."""
    print("🧹 Cleaning up old distribution files...")

    dist_dir = Path("../dist")
    if not dist_dir.exists():
        return

    # Keep only the latest 5 versions
    dist_files = sorted(dist_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
    files_to_keep = dist_files[:5]

    for file in dist_files:
        if file not in files_to_keep:
            file.unlink()
            print(f"  Removed: {file.name}")

def main():
    parser = argparse.ArgumentParser(description="Upload Sudarshan Engine to PyPI")
    parser.add_argument("--test", action="store_true",
                        help="Upload to Test PyPI first")
    parser.add_argument("--production", action="store_true",
                        help="Upload to production PyPI")
    parser.add_argument("--skip-validation", action="store_true",
                        help="Skip package validation")
    parser.add_argument("--cleanup", action="store_true",
                        help="Clean up old distribution files")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompts")

    args = parser.parse_args()

    print("📦 Sudarshan Engine PyPI Upload Tool")
    print("=" * 40)

    # Change to packaging directory
    os.chdir(os.path.dirname(__file__))

    # Clean up old files if requested
    if args.cleanup:
        cleanup_old_files()

    # Validate package
    if not args.skip_validation:
        validate_package()

    # Check prerequisites
    dist_files = check_prerequisites()

    # Test upload
    if args.test:
        if not test_upload("testpypi"):
            print("❌ Test upload failed. Fix issues before production upload.")
            sys.exit(1)

        print("\n🔍 Test package available at:")
        print("https://test.pypi.org/project/sudarshan-engine/")

        # Ask if user wants to continue to production
        if not args.production:
            if not args.yes:
                response = input("Continue to production upload? (yes/no): ").lower().strip()
                if response not in ['yes', 'y']:
                    print("Production upload cancelled")
                    return

    # Production upload
    if args.production or args.test:
        production_upload(skip_confirmation=args.yes)

        print("\n🎉 Package uploaded successfully!")
        print("📦 Available at: https://pypi.org/project/sudarshan-engine/")
        print("📖 Install with: pip install sudarshan-engine")

    else:
        print("ℹ️  Use --test to upload to Test PyPI first")
        print("ℹ️  Use --production to upload to production PyPI")

if __name__ == "__main__":
    main()