Quick Start Guide
==================

Get started with Sudarshan Engine in minutes! This guide shows you how to create your first quantum-safe encrypted file.

.. contents::
   :local:
   :depth: 2

Prerequisites
=============

Before starting, ensure you have:

- **Python 3.8+** installed
- **Sudarshan Engine** installed (see :doc:`installation`)
- **Basic command line knowledge**

.. code-block:: bash

   # Verify installation
   python --version
   sudarshan --version

Your First Encrypted File
=========================

Let's create your first quantum-safe encrypted file in 3 simple steps!

**Step 1: Create a test file**

.. code-block:: bash

   # Create a simple text file
   echo "Hello, Quantum World! 🌍" > message.txt

   # Verify the file was created
   cat message.txt

**Step 2: Encrypt the file**

.. code-block:: bash

   # Encrypt with Sudarshan Engine
   sudarshan spq_create --input message.txt --output secret.spq --password mySecretPassword123

   # Check the encrypted file
   ls -la secret.spq

You should see output like:

.. code-block::

   📁 Creating quantum-safe file...
   🔐 Using Kyber1024 for key encapsulation
   📝 Using Dilithium5 for signatures
   ✅ File encrypted successfully: secret.spq

**Step 3: Decrypt and verify**

.. code-block:: bash

   # Decrypt the file
   sudarshan spq_read --input secret.spq --password mySecretPassword123

You should see:

.. code-block::

   🔓 Decrypting quantum-safe file...
   ✅ Signature verified (Dilithium5)
   ✅ Hash verified (SHA3-512)
   📄 Original message: Hello, Quantum World! 🌍

🎉 **Congratulations!** You've just created and decrypted your first quantum-safe file!

Understanding the Output
=========================

When you encrypt a file, Sudarshan Engine shows:

- **Algorithm used**: Kyber1024 (quantum-safe key encapsulation)
- **Signature method**: Dilithium5 (quantum-safe digital signatures)
- **File size**: Original vs encrypted size
- **Security level**: Basic, Standard, High, or Critical

The encrypted ``.spq`` file contains:

- **Quantum-safe encryption** using NIST-approved algorithms
- **Tamper-evident integrity** with SHA3-512 hashing
- **Authenticated origin** with PQC digital signatures
- **Self-describing format** with embedded metadata

Python SDK Quick Start
======================

For programmatic use, here's how to use the Python SDK:

**Basic Encryption:**

.. code-block:: python

   from sudarshan import spq_create, spq_read

   # Your data
   secret_data = b"This is my secret message!"
   password = "mySecurePassword123"

   # Create metadata
   metadata = {
       "creator": "MyApp",
       "purpose": "secure_communication",
       "created_at": "2025-09-02T11:30:02Z"
   }

   # Encrypt
   result = spq_create(
       filepath="secret.spq",
       metadata=metadata,
       payload=secret_data,
       password=password
   )

   print(f"✅ Encrypted file created: {result['filepath']}")

**Basic Decryption:**

.. code-block:: python

   # Decrypt
   result = spq_read(
       filepath="secret.spq",
       password=password
   )

   print(f"📄 Decrypted data: {result['payload'].decode()}")
   print(f"📝 Metadata: {result['metadata']}")

Advanced Examples
=================

**Custom Algorithms:**

.. code-block:: python

   from sudarshan import spq_create

   # Use specific algorithms
   result = spq_create(
       filepath="custom.spq",
       metadata={"algorithm": "kyber768", "signature": "falcon1024"},
       payload=b"Custom algorithm example",
       password="password",
       algorithm="kyber768",
       signature="falcon1024"
   )

**File Compression:**

.. code-block:: python

   # Compress large files automatically
   result = spq_create(
       filepath="large.spq",
       metadata={"compression": "zstd"},
       payload=large_data,
       password="password",
       compress=True,
       compression_algo="zstd"
   )

**Batch Operations:**

.. code-block:: bash

   # Encrypt multiple files
   for file in *.txt; do
       sudarshan spq_create --input "$file" --output "${file%.txt}.spq" --password mypassword
   done

   # List encrypted files
   ls -la *.spq

Security Best Practices
=======================

**🔐 Password Security:**

- Use **strong, unique passwords** (12+ characters)
- Include **uppercase, lowercase, numbers, symbols**
- Never reuse passwords across different files
- Consider using **password managers**

**🔑 Key Management:**

- Store passwords securely (not in plain text)
- Use **hardware security modules** when available
- Rotate passwords periodically
- Never share encryption keys

**📁 File Handling:**

- Verify file integrity after transfer
- Use secure channels for file transmission
- Backup encrypted files regularly
- Delete temporary files securely

**🔒 Operational Security:**

- Work in **trusted environments**
- Use **full-disk encryption** on your devices
- Keep Sudarshan Engine **updated**
- Monitor for **suspicious activity**

Desktop Application
===================

If you prefer a graphical interface:

**Launch Desktop App:**

.. code-block:: bash

   # Launch the desktop application
   sudarshan gui

**Or run directly:**

.. code-block:: bash

   # Linux
   ./desktop_gui/SudarshanEngine

   # macOS
   open desktop_gui/SudarshanEngine.app

   # Windows
   desktop_gui\SudarshanEngine.exe

The desktop app provides:

- **Drag & drop** file encryption
- **Visual progress** indicators
- **Batch processing** capabilities
- **Password strength** meter
- **File browser** integration

Web Interface
=============

For web-based encryption:

**Start Web Server:**

.. code-block:: bash

   # Start local web server
   sudarshan web

**Access Interface:**

Open your browser to: ``http://localhost:8080``

The web interface offers:

- **Browser-based encryption** (client-side)
- **File upload/download**
- **Real-time progress** tracking
- **Mobile-friendly** design
- **Offline capability**

Command Line Reference
======================

**Core Commands:**

.. code-block:: bash

   # Get help
   sudarshan --help

   # Show version
   sudarshan --version

   # Create encrypted file
   sudarshan spq_create --input FILE --output FILE.spq --password PASSWORD

   # Read encrypted file
   sudarshan spq_read --input FILE.spq --password PASSWORD

   # List file information
   sudarshan info --input FILE.spq

   # Verify file integrity
   sudarshan verify --input FILE.spq

**Advanced Options:**

.. code-block:: bash

   # Custom algorithms
   sudarshan spq_create --input file.txt --output file.spq --password pass \
           --algorithm kyber768 --signature falcon1024

   # Compression
   sudarshan spq_create --input large_file.dat --output large.spq --password pass \
           --compress --compression zstd

   # Batch processing
   sudarshan batch --input-dir ./files --output-dir ./encrypted --password pass

   # Hardware security
   sudarshan spq_create --input file.txt --output file.spq --password pass \
           --hsm --tpm

Troubleshooting
===============

**Common Issues:**

**❌ "Command not found"**

.. code-block:: bash

   # Install Sudarshan Engine
   pip install sudarshan-engine

   # Or check PATH
   which sudarshan

**❌ "Invalid password"**

- Verify password is correct (case-sensitive)
- Check for extra spaces
- Try copy-pasting the password

**❌ "File not found"**

.. code-block:: bash

   # Check file exists
   ls -la message.txt

   # Use absolute paths
   sudarshan spq_create --input /full/path/message.txt --output secret.spq

**❌ "Permission denied"**

.. code-block:: bash

   # Fix permissions
   chmod 644 message.txt
   chmod 755 .  # Directory permissions

**❌ "Memory error"**

- For large files, use streaming mode
- Increase system memory
- Process files in smaller chunks

**❌ "Network timeout"**

- Check internet connection
- Use offline mode if available
- Try again later

Getting Help
============

**Documentation:**
- **Full Documentation**: https://docs.sudarshan.engine
- **API Reference**: :doc:`api/crypto`
- **Examples**: :doc:`examples/basic_usage`

**Community Support:**
- **GitHub Issues**: https://github.com/sudarshan-engine/sudarshan-engine/issues
- **Discussions**: https://github.com/sudarshan-engine/sudarshan-engine/discussions
- **Slack**: https://sudarshan-engine.slack.com

**Professional Support:**
- **Enterprise Support**: enterprise@sudarshan.engine
- **Security Issues**: security@sudarshan.engine
- **Bug Reports**: bugs@sudarshan.engine

Next Steps
==========

Now that you've created your first quantum-safe file, explore:

1. **Advanced Features**: Custom algorithms, compression, batch processing
2. **Integration Options**: Python SDK, REST API, Docker
3. **Security Features**: Hardware security, multi-factor authentication
4. **Use Cases**: Wallets, databases, secure communication

**Ready to dive deeper?**

- **Learn about the architecture**: :doc:`architecture`
- **Explore tutorials**: :doc:`tutorials/wallet_integration`
- **Check security guides**: :doc:`security/threat_model`

.. tip::
   For production use, always use strong passwords and keep your Sudarshan Engine installation updated.

.. note::
   Sudarshan Engine is designed to be quantum-resistant. Your encrypted files will remain secure even against future quantum computers!

.. warning::
   Never share your encryption passwords or keys. Always use secure channels for password communication.