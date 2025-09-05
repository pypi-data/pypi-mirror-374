Wallet Integration Tutorial
============================

Learn how to integrate Sudarshan Engine with cryptocurrency wallets for quantum-safe protection.

.. contents::
   :local:
   :depth: 2

Overview
========

Cryptocurrency wallets are prime targets for quantum attacks. This tutorial shows how to protect Bitcoin, Ethereum, and other cryptocurrency wallets using Sudarshan Engine's quantum-safe encryption.

**What You'll Learn:**
- Protect private keys with quantum-safe encryption
- Secure wallet backups and exports
- Implement multi-factor authentication
- Create secure transaction workflows

Prerequisites
=============

- Sudarshan Engine installed
- Basic cryptocurrency wallet (Bitcoin Core, Electrum, etc.)
- Understanding of wallet private keys and seed phrases

.. code-block:: bash

   # Verify installation
   sudarshan --version

   # Check crypto capabilities
   python -c "from sudarshan.crypto import QuantumSafeCrypto; print('✅ Ready')"

Protecting Private Keys
=======================

**Step 1: Export Wallet Data**

.. warning::
   Never export private keys on insecure systems. Use an air-gapped computer if possible.

For Bitcoin Core:

.. code-block:: bash

   # Backup wallet.dat (contains all private keys)
   bitcoin-cli backupwallet backup.dat

For Electrum:

.. code-block:: bash

   # Export seed phrase (write down securely)
   # Note: Never store seed phrases digitally unencrypted

**Step 2: Create Quantum-Safe Backup**

.. code-block:: python

   from sudarshan import spq_create
   import os

   # Read wallet backup file
   with open('backup.dat', 'rb') as f:
       wallet_data = f.read()

   # Create comprehensive metadata
   metadata = {
       "wallet_type": "bitcoin_core",
       "created_at": "2025-09-02T11:30:35Z",
       "algorithm": "kyber1024",
       "signature": "dilithium5",
       "purpose": "wallet_backup",
       "network": "mainnet",
       "description": "Bitcoin Core wallet backup - Quantum Safe"
   }

   # Encrypt with maximum security
   result = spq_create(
       filepath="bitcoin_wallet_backup.spq",
       metadata=metadata,
       payload=wallet_data,
       password="YourUltraSecurePassword123!",
       algorithm="kyber1024",
       signature="dilithium5",
       compress=True
   )

   print(f"✅ Wallet backup secured: {result['filepath']}")

**Step 3: Verify Backup Integrity**

.. code-block:: bash

   # Verify the encrypted file
   sudarshan verify --input bitcoin_wallet_backup.spq

   # Check file information
   sudarshan info --input bitcoin_wallet_backup.spq

Seed Phrase Protection
======================

**Secure Seed Phrase Storage:**

.. code-block:: python

   from sudarshan import spq_create
   import json

   # Secure seed phrase storage
   seed_data = {
       "wallet_name": "My Bitcoin Wallet",
       "seed_phrase": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
       "derivation_path": "m/44'/0'/0'/0",
       "created_at": "2025-09-02T11:30:35Z",
       "backup_locations": ["safe_deposit_box", "encrypted_drive"],
       "recovery_instructions": "Store in multiple secure locations"
   }

   metadata = {
       "type": "seed_phrase_backup",
       "algorithm": "kyber1024",
       "signature": "dilithium5",
       "encryption_level": "maximum",
       "access_requirements": "physical_security_required"
   }

   # Create encrypted seed phrase backup
   result = spq_create(
       filepath="seed_phrase_backup.spq",
       metadata=metadata,
       payload=json.dumps(seed_data).encode(),
       password="SeedPhraseMasterPassword2025!",
       compress=True
   )

Multi-Factor Wallet Protection
==============================

**Hardware + Software Protection:**

.. code-block:: python

   from sudarshan.protocols import OuterVault
   from sudarshan import spq_create

   # Initialize vault with MFA
   vault = OuterVault()

   # Define authentication factors
   factors = [
       {
           "type": "password",
           "strength": "high",
           "last_changed": "2025-09-02"
       },
       {
           "type": "hardware_token",
           "model": "yubikey_5c",
           "serial": "12345678"
       },
       {
           "type": "biometric",
           "method": "fingerprint",
           "device": "macbook_touchbar"
       }
   ]

   # Create MFA-protected wallet session
   session = vault.create_mfa_session(factors)

   # Encrypt wallet with MFA protection
   wallet_data = b"your_wallet_private_key_data"

   metadata = {
       "protection_level": "mfa_enabled",
       "factors_required": len(factors),
       "session_id": session['session_id'],
       "hardware_security": True
   }

   result = spq_create(
       filepath="mfa_wallet.spq",
       metadata=metadata,
       payload=wallet_data,
       password="MFAProtectedPassword!",
       algorithm="kyber1024"
   )

Transaction Security
====================

**Secure Transaction Signing:**

.. code-block:: python

   from sudarshan.protocols import TransactionCapsule
   from sudarshan import spq_create

   # Initialize transaction capsule
   tx_capsule = TransactionCapsule()

   # Create secure transaction
   transaction_data = {
       "type": "bitcoin_transaction",
       "amount": "0.001",
       "recipient": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
       "fee": "0.00001",
       "timestamp": "2025-09-02T11:30:35Z"
   }

   # Create one-time transaction capsule
   capsule = tx_capsule.create_secure_transaction(
       transaction_data=transaction_data,
       security_level="high"
   )

   # Encrypt transaction capsule
   metadata = {
       "transaction_type": "bitcoin_send",
       "capsule_id": capsule['capsule_id'],
       "one_time_use": True,
       "expires_at": capsule['expires_at']
   }

   result = spq_create(
       filepath="secure_transaction.spq",
       metadata=metadata,
       payload=json.dumps(capsule).encode(),
       password="TransactionPassword123!",
       compress=True
   )

Cold Storage Integration
========================

**Air-Gapped Wallet Protection:**

.. code-block:: python

   # For air-gapped (offline) wallets
   from sudarshan import spq_create

   # Cold storage wallet data
   cold_wallet = {
       "private_key": "L1uyy5qTuGrVXrmrsvHWHgVzW9kKdrp27wBC7Vs6nZDTF2BRUVs",
       "public_key": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
       "address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
       "network": "bitcoin_mainnet",
       "cold_storage": True,
       "last_access": "2025-09-02T11:30:35Z"
   }

   metadata = {
       "storage_type": "cold_storage",
       "air_gapped": True,
       "physical_security": "safe_deposit_box",
       "backup_copies": 3,
       "recovery_procedure": "Multi-signature required"
   }

   # Create quantum-safe cold storage backup
   result = spq_create(
       filepath="cold_wallet_backup.spq",
       metadata=metadata,
       payload=json.dumps(cold_wallet).encode(),
       password="ColdStorageMasterKey2025!",
       algorithm="kyber1024",
       signature="dilithium5"
   )

Hardware Wallet Integration
===========================

**Ledger/Trezor Integration:**

.. code-block:: python

   from sudarshan.protocols import IsolationRoom
   from sudarshan import spq_create

   # Initialize hardware isolation
   isolation = IsolationRoom()

   # Hardware wallet data structure
   hw_wallet = {
       "device_type": "ledger_nano_x",
       "firmware_version": "2.1.0",
       "public_keys": [
           "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8"
       ],
       "derivation_paths": ["44'/0'/0'/0/0"],
       "security_features": ["pin_protection", "passphrase", "u2f"]
   }

   # Execute in hardware-secured environment
   result = isolation.execute_with_hardware_security(
       operation="encrypt_wallet_data",
       data=json.dumps(hw_wallet).encode(),
       hardware_requirements=["hsm_available", "secure_enclave"]
   )

   metadata = {
       "hardware_wallet": True,
       "device_type": "ledger_nano_x",
       "hardware_security": True,
       "pin_required": True,
       "passphrase_required": True
   }

   final_result = spq_create(
       filepath="hardware_wallet_backup.spq",
       metadata=metadata,
       payload=result['encrypted_data'],
       password="HardwareWalletPassword!",
       algorithm="kyber1024"
   )

Multi-Currency Wallet Support
==============================

**Ethereum Wallet Protection:**

.. code-block:: python

   # Ethereum wallet data
   eth_wallet = {
       "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
       "private_key": "0xa8b2f1c3d4e5f6789012345678901234567890123456789012345678901234567890",
       "mnemonic": "witch collapse practice feed shame open despair creek road again ice least",
       "derivation_path": "m/44'/60'/0'/0/0",
       "network": "ethereum_mainnet"
   }

   metadata = {
       "cryptocurrency": "ethereum",
       "wallet_type": "metamask_compatible",
       "erc20_tokens": ["USDT", "UNI", "LINK"],
       "defi_protocols": ["uniswap", "compound"]
   }

   result = spq_create(
       filepath="ethereum_wallet.spq",
       metadata=metadata,
       payload=json.dumps(eth_wallet).encode(),
       password="EthereumSecurePassword!",
       algorithm="kyber1024"
   )

**Multi-Currency Portfolio:**

.. code-block:: python

   # Multi-currency wallet portfolio
   portfolio = {
       "bitcoin": {
           "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
           "balance": "0.005",
           "last_transaction": "2025-09-01T10:30:00Z"
       },
       "ethereum": {
           "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
           "balance": "1.25",
           "tokens": {"USDT": 1000, "UNI": 50}
       },
       "portfolio_value_usd": 1250.75,
       "last_updated": "2025-09-02T11:30:35Z"
   }

   metadata = {
       "portfolio_type": "multi_currency",
       "cryptocurrencies": ["BTC", "ETH", "USDT", "UNI"],
       "total_value_usd": 1250.75,
       "backup_frequency": "daily",
       "recovery_priority": "high"
   }

   result = spq_create(
       filepath="crypto_portfolio.spq",
       metadata=metadata,
       payload=json.dumps(portfolio).encode(),
       password="PortfolioMasterKey2025!",
       compress=True
   )

Security Best Practices
=======================

**Wallet Security:**

1. **Never store unencrypted keys** on internet-connected devices
2. **Use strong, unique passwords** for each wallet
3. **Enable multi-factor authentication** when possible
4. **Regular backups** with quantum-safe encryption
5. **Test recovery procedures** regularly

**Operational Security:**

.. code-block:: bash

   # Create secure working directory
   mkdir -p ~/secure_wallet_work
   cd ~/secure_wallet_work

   # Set restrictive permissions
   chmod 700 ~/secure_wallet_work

   # Work with encrypted files only
   sudarshan spq_create --input wallet.dat --output wallet.spq --password $(openssl rand -hex 32)

**Backup Strategy:**

.. code-block:: bash

   # Create multiple encrypted backups
   for i in {1..3}; do
       sudarshan spq_create --input wallet.dat --output "wallet_backup_$i.spq" --password "UniquePassword$i"
   done

   # Store in different secure locations
   # 1. Encrypted external drive
   # 2. Secure cloud storage (encrypted)
   # 3. Physical safe deposit box

Recovery Procedures
===================

**Emergency Recovery:**

.. code-block:: bash

   # Decrypt wallet backup
   sudarshan spq_read --input wallet_backup_1.spq --password "YourRecoveryPassword"

   # Verify integrity
   sudarshan verify --input wallet_backup_1.spq

   # Import to wallet software
   # (Follow wallet-specific recovery procedures)

**Multi-Signature Recovery:**

.. code-block:: python

   from sudarshan.protocols import OuterVault

   # Multi-signature recovery
   vault = OuterVault()

   recovery_factors = [
       {"type": "password", "holder": "primary_owner"},
       {"type": "password", "holder": "trusted_family"},
       {"type": "hardware_token", "holder": "lawyer"}
   ]

   # Require multiple factors for recovery
   recovery_session = vault.create_recovery_session(recovery_factors)

   # Decrypt only with all required approvals
   recovered_wallet = vault.recover_with_approvals(
       encrypted_wallet="wallet.spq",
       recovery_session=recovery_session,
       required_approvals=2
   )

Integration Examples
====================

**Wallet Software Integration:**

.. code-block:: python

   class QuantumSafeWallet:
       def __init__(self, wallet_path):
           self.wallet_path = wallet_path
           self.sudarshan = SudarshanEngine()

       def secure_backup(self, password):
           """Create quantum-safe backup"""
           with open(self.wallet_path, 'rb') as f:
               wallet_data = f.read()

           metadata = {
               "wallet_software": "Bitcoin Core",
               "version": "25.0",
               "backup_type": "full_wallet"
           }

           return self.sudarshan.spq_create(
               filepath=f"{self.wallet_path}.spq",
               metadata=metadata,
               payload=wallet_data,
               password=password
           )

       def secure_transaction(self, tx_data, password):
           """Create secure transaction"""
           metadata = {
               "transaction_type": "bitcoin_send",
               "amount_btc": tx_data['amount'],
               "fee_satoshi": tx_data['fee']
           }

           return self.sudarshan.spq_create(
               filepath=f"transaction_{tx_data['txid']}.spq",
               metadata=metadata,
               payload=json.dumps(tx_data).encode(),
               password=password
           )

Monitoring and Auditing
=======================

**Security Monitoring:**

.. code-block:: python

   from sudarshan.security import SecurityMonitor

   monitor = SecurityMonitor()

   # Monitor wallet access
   monitor.watch_file_access("wallet.spq")

   # Log security events
   monitor.log_event({
       "event_type": "wallet_access",
       "timestamp": "2025-09-02T11:30:35Z",
       "access_type": "decryption",
       "security_level": "high"
   })

   # Generate security report
   report = monitor.generate_security_report()
   print(f"Security Score: {report['overall_score']}/100")

Next Steps
==========

- **Database Security**: :doc:`database_security`
- **Payment System Integration**: :doc:`payment_system`
- **Custom Protocol Development**: :doc:`custom_protocols`
- **API Integration**: :doc:`../guides/api_integration`

.. tip::
   Always test your recovery procedures with small amounts before securing large holdings.

.. warning::
   Quantum-safe encryption protects against future threats, but doesn't eliminate the need for good operational security practices.

.. note::
   Regular backups with Sudarshan Engine ensure your crypto assets remain secure against both current and future threats.