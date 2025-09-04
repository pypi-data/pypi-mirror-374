Sudarshan Engine Documentation
===============================

.. image:: _static/logo.png
   :alt: Sudarshan Engine Logo
   :align: center

**Universal Quantum-Safe Cybersecurity Engine**

Sudarshan Engine is a comprehensive, open-core cybersecurity solution that provides quantum-resistant protection for any digital asset or application. Built with a unique "Box-in-a-Box" architecture, it offers unparalleled security against current and future threats.

🚀 **Key Features**
==================

.. list-table::
   :header-rows: 1
   :widths: 20 30

   * - Feature
     - Description
   * - **Quantum-Safe**
     - NIST-approved PQC algorithms (Kyber, Dilithium, Falcon)
   * - **Universal**
     - Secures wallets, databases, payment systems, and any digital service
   * - **Box-in-a-Box**
     - Four-layer security model with independent protection
   * - **Open-Core**
     - Free CLI/SDK with commercial API extensions
   * - **Multi-Platform**
     - Linux, macOS, Windows, and cloud deployments

📋 **Table of Contents**
=======================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   architecture

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/cli_usage
   guides/desktop_app
   guides/web_interface
   guides/api_integration

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   tutorials/wallet_integration
   tutorials/database_security
   tutorials/payment_system
   tutorials/custom_protocols

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/crypto
   api/spq_format
   api/protocols
   api/security

.. toctree::
   :maxdepth: 2
   :caption: Security

   security/threat_model
   security/best_practices
   security/compliance
   security/auditing

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_usage
   examples/advanced_scenarios
   examples/integration_patterns

.. toctree::
   :maxdepth: 2
   :caption: Community & Support

   community/contributing
   community/faq
   community/troubleshooting

🎯 **Quick Start**
=================

**Install Sudarshan Engine:**

.. code-block:: bash

   # From PyPI
   pip install sudarshan-engine

   # From source
   git clone https://github.com/sudarshan-engine/sudarshan-engine
   cd sudarshan-engine
   pip install -e .

**Create your first quantum-safe file:**

.. code-block:: python

   from sudarshan import spq_create

   # Create metadata
   metadata = {
       "creator": "MyApp",
       "created_at": "2025-09-02T11:29:01Z",
       "algorithm": "Kyber1024",
       "signature": "Dilithium5"
   }

   # Create quantum-safe file
   spq_create("secure.spq", metadata, b"secret data", "password")

**Use the CLI:**

.. code-block:: bash

   # Create encrypted file
   sudarshan spq_create --input document.txt --output secure.spq --password mypassword

   # Read encrypted file
   sudarshan spq_read --input secure.spq --password mypassword

🔒 **Security Overview**
=======================

Sudarshan Engine implements a revolutionary "Box-in-a-Box" security architecture:

.. image:: _static/box_in_box_diagram.png
   :alt: Box-in-a-Box Security Model
   :align: center

**Four Security Layers:**

1. **Inner Shield** - PQC wrapper for legacy assets
2. **Outer Vault** - Multi-factor authentication with PQC
3. **Isolation Room** - Hardware-secured enclave operations
4. **Transaction Capsule** - One-time stateless transactions

**Cryptographic Foundation:**

- **Key Encapsulation**: Kyber (NIST FIPS 203)
- **Digital Signatures**: Dilithium/Falcon (NIST FIPS 204/205)
- **Symmetric Encryption**: AES-256-GCM/ChaCha20-Poly1305
- **Hash Functions**: SHA3-512 (NIST FIPS 202)

📊 **Performance Metrics**
==========================

.. list-table::
   :header-rows: 1
   :widths: 25 15 15 15

   * - Operation
     - Kyber512
     - Kyber1024
     - Target
   * - Key Generation
     - < 50ms
     - < 100ms
     - < 200ms
   * - Encryption
     - < 25ms
     - < 50ms
     - < 100ms
   * - Decryption
     - < 25ms
     - < 50ms
     - < 100ms
   * - Signature
     - < 10ms
     - < 20ms
     - < 50ms
   * - Verification
     - < 5ms
     - < 10ms
     - < 25ms

🏢 **Use Cases**
===============

**🔐 Quantum-Safe Wallets**
   Secure Bitcoin, Ethereum, and other cryptocurrency wallets against quantum attacks.

**🗄️ Database Security**
   Encrypt sensitive data at rest and in transit with quantum-resistant algorithms.

**💳 Payment Systems**
   Protect financial transactions with stateless, one-time cryptographic operations.

**🏥 Healthcare**
   Secure patient data and medical records with HIPAA-compliant encryption.

**🏛️ Government**
   Protect classified information with FIPS-compliant quantum-safe cryptography.

**🏭 IoT Security**
   Secure Internet of Things devices and industrial control systems.

🌟 **Why Sudarshan Engine?**
===========================

**Unmatched Security:**
   Four-layer defense-in-depth with quantum-resistant cryptography.

**Developer Friendly:**
   Simple API, comprehensive documentation, and active community support.

**Future Proof:**
   Built for the quantum computing era with NIST-approved algorithms.

**Production Ready:**
   Enterprise-grade security with comprehensive testing and auditing.

**Open Source First:**
   Transparent, auditable code with commercial extensions for enterprise needs.

📞 **Support & Community**
==========================

- **📖 Documentation**: You're reading it!
- **🐛 Issue Tracker**: `https://github.com/sudarshan-engine/sudarshan-engine/issues`
- **💬 Discussions**: `https://github.com/sudarshan-engine/sudarshan-engine/discussions`
- **📧 Email**: support@sudarshan.engine
- **🎯 Slack**: `https://sudarshan-engine.slack.com`
- **🐦 Twitter**: `@SudarshanEngine`

🤝 **Contributing**
==================

We welcome contributions! See our :doc:`Contributing Guide <community/contributing>` for details.

**Quick Links:**
   - :doc:`Installation <installation>`
   - :doc:`Quick Start <quickstart>`
   - :doc:`API Reference <api/crypto>`
   - :doc:`Security Guide <security/threat_model>`

---

**🚀 Ready to secure your digital assets? Let's get started!**

.. note::
   Sudarshan Engine is production-ready and actively maintained. For enterprise support and commercial licensing, contact our sales team.

.. warning::
   Always keep your cryptographic keys secure and never share them. Use strong, unique passwords for all operations.

.. tip::
   Start with our :doc:`Quick Start Guide <quickstart>` to create your first quantum-safe encrypted file in minutes!