# Security Policy

## 🔒 Security Overview

The Sudarshan Engine is a quantum-safe cryptographic library that implements post-quantum cryptography (PQC) algorithms. We take security seriously and welcome responsible disclosure of security vulnerabilities.

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability in the Sudarshan Engine, please help us by reporting it responsibly.

### 📧 How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Email**: yash02.prof@gmail.com
- **Subject**: [SECURITY] Vulnerability Report - Sudarshan Engine

### 📋 What to Include

When reporting a vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Impact**: Potential impact and severity
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Proof of Concept**: Code or other evidence demonstrating the vulnerability
5. **Affected Versions**: Which versions are affected
6. **Mitigation**: Any suggested fixes or workarounds

### ⏰ Response Timeline

We will acknowledge your report within **48 hours** and provide a more detailed response within **7 days** indicating our next steps.

We will keep you informed about our progress throughout the process of fixing the vulnerability.

## 🎯 Scope

### In Scope
- Core cryptographic implementations in `sudarshan/crypto.py`
- Protocol implementations in `sudarshan/protocols.py`
- SPQ format handling in `sudarshan/spq_format.py`
- Security audit tools in `security/`
- Web interface security in `web_interface/`
- API daemon security in `api_daemon/`
- Desktop GUI security in `desktop_gui/`

### Out of Scope
- Third-party dependencies (please report to respective maintainers)
- Configuration issues in deployment environments
- Denial of service attacks requiring massive computational resources
- Issues in development/testing environments only

## 🏆 Recognition

We appreciate security researchers who help keep our users safe. With your permission, we will:

- Acknowledge your contribution in our security advisory
- Add you to our Hall of Fame (if you wish)
- Send you swag or other recognition (when available)

## 🔧 Security Best Practices

### For Users
- Always use the latest stable version
- Verify cryptographic signatures when available
- Use strong, unique keys for encryption
- Follow the production deployment guidelines in `PRODUCTION_DEPLOYMENT.md`

### For Contributors
- Run security tests before submitting changes
- Follow secure coding practices
- Document security considerations in code comments
- Update tests when making security-related changes

## 📊 Security Updates

Security updates will be:
- Released as soon as possible after a fix is developed
- Documented in the `CHANGELOG.md`
- Announced through our GitHub releases
- Tagged with appropriate severity levels

## 🆘 Emergency Contact

For critical vulnerabilities that could cause immediate harm:
- **Emergency Email**: yash02.prof@gmail.com
- **Phone**: Available upon request for verified researchers

## 📜 Legal

This security policy is governed by our main license terms. By participating in our security disclosure program, you agree to act in good faith and not to:
- Perform unauthorized testing
- Disclose vulnerabilities before they are fixed
- Demand payment for vulnerability reports
- Engage in any illegal activities

## 🙏 Acknowledgments

We thank the security research community for helping make cryptography safer for everyone.

---

*Last updated: September 2024*