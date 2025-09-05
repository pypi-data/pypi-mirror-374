#!/usr/bin/env python3
"""
Sudarshan Engine - Security Audit Tool

This script performs automated security checks on the codebase
to identify potential vulnerabilities and security issues.
"""

import os
import re
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Security audit tool for Sudarshan Engine"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []

    def audit(self) -> Dict[str, List[str]]:
        """Run complete security audit"""
        logger.info("Starting security audit...")

        self.check_hardcoded_secrets()
        self.check_file_permissions()
        self.check_dependency_security()
        self.check_crypto_implementation()
        self.check_input_validation()
        self.check_error_handling()

        return {
            'issues': self.issues,
            'warnings': self.warnings
        }

    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets and keys"""
        logger.info("Checking for hardcoded secrets...")

        # Files to check
        sensitive_files = [
            'my_keys.json',
            '*.key',
            '*.pem',
            'secrets/',
            'keys/',
            '*.env'
        ]

        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.exists():
                    self.issues.append(f"Potentially sensitive file found: {file_path}")

        # Check for hardcoded patterns in code
        code_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]

        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in code_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.warnings.append(f"Potential hardcoded credential in {py_file}: {matches[:3]}")
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")

    def check_file_permissions(self):
        """Check file permissions for security issues"""
        logger.info("Checking file permissions...")

        sensitive_extensions = ['.key', '.pem', '.env', '.p12', '.pfx']

        for ext in sensitive_extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                if file_path.exists():
                    # Check if file is readable by others
                    mode = oct(file_path.stat().st_mode)[-3:]
                    if mode[1] != '0' or mode[2] != '0':  # group/other has permissions
                        self.issues.append(f"Insecure permissions on {file_path}: {mode}")

    def check_dependency_security(self):
        """Check for insecure dependencies"""
        logger.info("Checking dependencies...")

        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read()

                # Check for known vulnerable packages (basic check)
                vulnerable_packages = [
                    'pycrypto',  # Should use cryptography
                    'simple-crypt',
                    'pycryptodome<3.10.0'  # Older versions have vulnerabilities
                ]

                for package in vulnerable_packages:
                    if package in content:
                        self.warnings.append(f"Potentially vulnerable package found: {package}")
            except Exception as e:
                logger.warning(f"Could not read requirements.txt: {e}")

    def check_crypto_implementation(self):
        """Check cryptographic implementation security"""
        logger.info("Checking crypto implementation...")

        crypto_files = list(self.project_root.rglob('**/crypto.py')) + \
                      list(self.project_root.rglob('**/protocols.py'))

        for file_path in crypto_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for insecure practices
                insecure_patterns = [
                    r'secrets\.token_bytes\(12\)',  # Should be 16+ for AES
                    r'AES.*128',  # Should use AES-256
                    r'MD5',
                    r'SHA1',
                    r'random\.',
                    r'os\.urandom'
                ]

                for pattern in insecure_patterns:
                    if re.search(pattern, content):
                        self.warnings.append(f"Potentially insecure crypto pattern in {file_path}: {pattern}")

                # Check for secure patterns
                secure_patterns = [
                    r'hmac\.compare_digest',
                    r'constant_time',
                    r'AES.*256',
                    r'SHA3',
                    r'SHA256'
                ]

                secure_count = 0
                for pattern in secure_patterns:
                    if re.search(pattern, content):
                        secure_count += 1

                if secure_count < 2:
                    self.warnings.append(f"Limited secure crypto patterns found in {file_path}")

            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

    def check_input_validation(self):
        """Check for proper input validation"""
        logger.info("Checking input validation...")

        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for potential injection vulnerabilities
                dangerous_patterns = [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'os\.system\s*\(',
                    r'subprocess\.call\s*\(',
                    r'subprocess\.run\s*\('
                ]

                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        self.issues.append(f"Potentially dangerous function call in {py_file}: {pattern}")

            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")

    def check_error_handling(self):
        """Check error handling practices"""
        logger.info("Checking error handling...")

        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for bare except clauses
                if re.search(r'except\s*:', content):
                    self.warnings.append(f"Bare except clause found in {py_file} - may hide errors")

                # Check for proper logging of sensitive information
                sensitive_logging = [
                    r'print\s*\(.*password.*\)',
                    r'print\s*\(.*secret.*\)',
                    r'print\s*\(.*key.*\)',
                    r'log.*password',
                    r'log.*secret',
                    r'log.*key'
                ]

                for pattern in sensitive_logging:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.issues.append(f"Potential sensitive data logging in {py_file}: {pattern}")

            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")


def main():
    """Main audit function"""
    project_root = Path(__file__).parent.parent
    auditor = SecurityAuditor(project_root)

    results = auditor.audit()

    print("\n" + "="*60)
    print("SECURITY AUDIT RESULTS")
    print("="*60)

    if results['issues']:
        print(f"\n🚨 CRITICAL ISSUES ({len(results['issues'])}):")
        for issue in results['issues']:
            print(f"  • {issue}")

    if results['warnings']:
        print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"  • {warning}")

    if not results['issues'] and not results['warnings']:
        print("\n✅ No security issues found!")

    print("\n" + "="*60)

    # Return non-zero exit code if there are critical issues
    return len(results['issues'])


if __name__ == "__main__":
    exit(main())