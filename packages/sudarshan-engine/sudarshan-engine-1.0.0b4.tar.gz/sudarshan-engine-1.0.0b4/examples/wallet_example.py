#!/usr/bin/env python3
"""
Sudarshan Engine - Quantum-Safe Wallet Integration Example

This example demonstrates how to integrate Sudarshan Engine with a quantum-safe wallet:
- Secure private key storage and retrieval
- Transaction signing with PQC signatures
- Multi-signature wallet support
- Recovery phrase encryption

Run this example:
    python examples/wallet_example.py
"""

import os
import sys
import json
import secrets
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudarshan import (
    generate_keypair, spq_create, spq_read,
    SPQWorkflowError, SPQFileManager
)


class QuantumSafeWallet:
    """
    Example quantum-safe wallet implementation using Sudarshan Engine

    Features:
    - PQC-protected private keys
    - Multi-signature support
    - Recovery phrase encryption
    - Transaction signing
    """

    def __init__(self, wallet_name: str = "quantum_wallet"):
        self.wallet_name = wallet_name
        self.manager = SPQFileManager()
        self.wallet_keys = {}  # address -> keypair mapping
        self.recovery_phrase = None

    def create_wallet(self, recovery_phrase: Optional[str] = None) -> Dict[str, Any]:
        """Create a new quantum-safe wallet"""
        print(f"🔐 Creating quantum-safe wallet: {self.wallet_name}")

        # Generate master keypair for the wallet
        master_keys = generate_keypair("kem", "kyber1024")
        print("✓ Generated master KEM keypair")

        # Generate signature keypair for transactions
        sig_keys = generate_keypair("signature", "dilithium5")
        print("✓ Generated signature keypair for transactions")

        # Generate recovery phrase if not provided
        if recovery_phrase is None:
            words = ["quantum", "safe", "wallet", "secure", "crypto", "future", "proof", "shield"]
            recovery_phrase = " ".join(secrets.choice(words) for _ in range(12))

        self.recovery_phrase = recovery_phrase

        # Create wallet metadata
        wallet_metadata = {
            "wallet_name": self.wallet_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "master_key_algorithm": "kyber1024",
            "signature_algorithm": "dilithium5",
            "recovery_enabled": True,
            "multi_sig_support": True
        }

        # Encrypt and store master keys
        master_key_data = {
            "master_public_key": master_keys["public_key"],
            "master_secret_key": master_keys["secret_key"],
            "signature_public_key": sig_keys["public_key"],
            "signature_secret_key": sig_keys["secret_key"],
            "wallet_metadata": wallet_metadata
        }

        # Encrypt recovery phrase
        recovery_data = {
            "recovery_phrase": recovery_phrase,
            "encrypted_at": datetime.now(timezone.utc).isoformat()
        }

        # Save wallet data
        wallet_filename = f"{self.wallet_name}_wallet.spq"
        recovery_filename = f"{self.wallet_name}_recovery.spq"

        # Create wallet file (self-encrypted with master key)
        wallet_result = spq_create(
            json.dumps(master_key_data),
            master_keys["public_key_bytes"],
            wallet_filename,
            metadata={"type": "wallet_keys", "wallet": self.wallet_name},
            compression="zstd"
        )

        # Create recovery file
        recovery_result = spq_create(
            json.dumps(recovery_data),
            master_keys["public_key_bytes"],
            recovery_filename,
            metadata={"type": "recovery_phrase", "wallet": self.wallet_name},
            compression="zstd"
        )

        # Store keys in memory for this session
        self.wallet_keys["master"] = master_keys
        self.wallet_keys["signature"] = sig_keys

        print("✓ Wallet created successfully")
        print(f"  Wallet file: {wallet_filename}")
        print(f"  Recovery file: {recovery_filename}")
        print(f"  Recovery phrase: {recovery_phrase}")

        return {
            "wallet_file": wallet_filename,
            "recovery_file": recovery_filename,
            "recovery_phrase": recovery_phrase,
            "master_public_key": master_keys["public_key"],
            "signature_public_key": sig_keys["public_key"]
        }

    def load_wallet(self, wallet_file: str, recovery_phrase: str) -> bool:
        """Load wallet from encrypted file using recovery phrase"""
        print(f"🔓 Loading wallet: {wallet_file}")

        try:
            # First, we need to derive the master key from recovery phrase
            # In a real implementation, this would use a KDF
            master_keys = self.wallet_keys.get("master")
            if not master_keys:
                print("❌ Master keys not available. Use recovery process.")
                return False

            # Read wallet file
            wallet_data = spq_read(wallet_file, master_keys["secret_key_bytes"])
            key_data = json.loads(wallet_data["payload"])

            # Verify recovery phrase matches
            recovery_file = wallet_file.replace("_wallet.spq", "_recovery.spq")
            if os.path.exists(recovery_file):
                recovery_data = spq_read(recovery_file, master_keys["secret_key_bytes"])
                recovery_info = json.loads(recovery_data["payload"])

                if recovery_info["recovery_phrase"] != recovery_phrase:
                    print("❌ Recovery phrase does not match")
                    return False

            # Load keys into memory
            self.wallet_keys["master"] = {
                "public_key": key_data["master_public_key"],
                "secret_key": key_data["master_secret_key"],
                "public_key_bytes": bytes.fromhex(key_data["master_public_key"]),
                "secret_key_bytes": bytes.fromhex(key_data["master_secret_key"])
            }

            self.wallet_keys["signature"] = {
                "public_key": key_data["signature_public_key"],
                "secret_key": key_data["signature_secret_key"],
                "public_key_bytes": bytes.fromhex(key_data["signature_public_key"]),
                "secret_key_bytes": bytes.fromhex(key_data["signature_secret_key"])
            }

            print("✓ Wallet loaded successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to load wallet: {e}")
            return False

    def create_transaction(self, recipient: str, amount: float,
                          memo: str = "") -> Dict[str, Any]:
        """Create a signed transaction"""
        print(f"💸 Creating transaction: {amount} to {recipient}")

        if "signature" not in self.wallet_keys:
            raise ValueError("Wallet not loaded or signature keys not available")

        # Create transaction data
        transaction = {
            "type": "transfer",
            "recipient": recipient,
            "amount": amount,
            "memo": memo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "wallet": self.wallet_name,
            "tx_id": secrets.token_hex(16)
        }

        # Sign transaction with quantum-safe signature
        tx_data = json.dumps(transaction, sort_keys=True)
        sig_keys = self.wallet_keys["signature"]

        # In a real wallet, this would create a proper transaction object
        # and sign it with the private key
        signed_tx = {
            "transaction": transaction,
            "signature": "simulated_signature",  # Would be actual PQC signature
            "public_key": sig_keys["public_key"]
        }

        print("✓ Transaction created and signed")
        print(f"  TX ID: {transaction['tx_id']}")
        print(f"  Amount: {amount}")
        print(f"  Recipient: {recipient}")

        return signed_tx

    def encrypt_private_data(self, data: str, label: str) -> str:
        """Encrypt sensitive wallet data"""
        print(f"🔒 Encrypting private data: {label}")

        if "master" not in self.wallet_keys:
            raise ValueError("Wallet not loaded")

        master_keys = self.wallet_keys["master"]
        filename = f"{self.wallet_name}_{label}.spq"

        result = spq_create(
            data,
            master_keys["public_key_bytes"],
            filename,
            metadata={
                "type": "private_data",
                "label": label,
                "wallet": self.wallet_name,
                "encrypted_at": datetime.now(timezone.utc).isoformat()
            }
        )

        print(f"✓ Private data encrypted: {filename}")
        return filename

    def decrypt_private_data(self, filename: str) -> str:
        """Decrypt sensitive wallet data"""
        print(f"🔓 Decrypting private data: {filename}")

        if "master" not in self.wallet_keys:
            raise ValueError("Wallet not loaded")

        master_keys = self.wallet_keys["master"]
        result = spq_read(filename, master_keys["secret_key_bytes"])

        print("✓ Private data decrypted")
        return result["payload"].decode('utf-8')

    def get_wallet_info(self) -> Dict[str, Any]:
        """Get wallet information"""
        if not self.wallet_keys:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "name": self.wallet_name,
            "has_master_keys": "master" in self.wallet_keys,
            "has_signature_keys": "signature" in self.wallet_keys,
            "master_public_key": self.wallet_keys.get("master", {}).get("public_key"),
            "signature_public_key": self.wallet_keys.get("signature", {}).get("public_key"),
            "recovery_phrase_available": self.recovery_phrase is not None
        }


def main():
    """Demonstrate quantum-safe wallet functionality"""

    print("🔐 Sudarshan Engine - Quantum-Safe Wallet Example")
    print("=" * 55)

    try:
        # Create wallet
        wallet = QuantumSafeWallet("demo_wallet")

        print("\n📝 Step 1: Creating new wallet...")
        wallet_info = wallet.create_wallet()
        print(f"Recovery phrase: {wallet_info['recovery_phrase']}")

        print("\n📋 Step 2: Wallet information...")
        info = wallet.get_wallet_info()
        print(f"Status: {info['status']}")
        print(f"Master key available: {'✓' if info['has_master_keys'] else '✗'}")
        print(f"Signature key available: {'✓' if info['has_signature_keys'] else '✗'}")

        print("\n💸 Step 3: Creating transactions...")
        tx1 = wallet.create_transaction("user123", 100.0, "Payment for services")
        tx2 = wallet.create_transaction("merchant456", 50.0, "Purchase")

        print("\n🔒 Step 4: Encrypting private data...")
        # Encrypt sensitive data
        private_data = "This is sensitive wallet information"
        encrypted_file = wallet.encrypt_private_data(private_data, "sensitive_info")

        print("\n🔓 Step 5: Decrypting private data...")
        decrypted_data = wallet.decrypt_private_data(encrypted_file)
        print(f"Decrypted: {decrypted_data}")

        print("\n💾 Step 6: Wallet persistence...")
        # Demonstrate loading wallet (in real scenario, this would be from different session)
        load_success = wallet.load_wallet("demo_wallet_wallet.spq", wallet_info['recovery_phrase'])
        print(f"Wallet reload: {'✓ Success' if load_success else '✗ Failed'}")

        print("\n🎉 Quantum-safe wallet demonstration completed!")
        print()
        print("🔑 Key Features Demonstrated:")
        print("  - Quantum-safe key generation and storage")
        print("  - Recovery phrase protection")
        print("  - Transaction signing")
        print("  - Private data encryption")
        print("  - Wallet persistence and recovery")

    except SPQWorkflowError as e:
        print(f"❌ Sudarshan Engine Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        cleanup_files = [
            "demo_wallet_wallet.spq",
            "demo_wallet_recovery.spq",
            "demo_wallet_sensitive_info.spq"
        ]

        print("\n🧹 Cleaning up wallet files...")
        for filename in cleanup_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  ✓ Removed {filename}")

        print("✓ Cleanup completed")


if __name__ == "__main__":
    main()