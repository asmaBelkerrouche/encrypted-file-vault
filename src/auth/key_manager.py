# # src/auth/key_manager.py
# # src/crypto/engine.py

"""
Key Manager - Handles all cryptographic key operations
"""

import os
import json
import base64
from pathlib import Path
from src.crypto.engine import CryptoEngine

class KeyManager:
    def __init__(self, vault_path: str = "./vault_data"):
        self.vault_path = Path(vault_path)
        self.crypto = CryptoEngine()
        print(" Key Manager Initialized")
    
    def initialize_vault(self, password: str) -> bool:
        """Create a new encrypted vault"""
        print(" Initializing new vault...")
        
        # Create vault directory
        self.vault_path.mkdir(exist_ok=True)
        
        # Generate KEK (Key Encryption Key) from password
        print("   Deriving master key from password...")
        master_key, salt = self.crypto.derive_key(password)
        
        # Generate a random KEK
        kek = self.crypto.generate_file_key()
        
        # Encrypt the KEK with master key
        encrypted_kek = self.crypto.encrypt_data(kek, master_key)
        
        # Save encrypted data
        print("   Saving encrypted keys...")
        with open(self.vault_path / "master_key.enc", 'wb') as f:
            f.write(salt + encrypted_kek)
        
        # Create empty metadata
        metadata = {}
        self.save_metadata(metadata, kek)
        
        # Save password hint (optional, not secure)
        with open(self.vault_path / "password_hint.txt", 'w') as f:
            f.write(f"Vault created at: {Path.cwd()}\n")
            f.write(f"Password reminder: Set password as '{password}'\n")
        
        print(" Vault initialized successfully!")
        return True
    
    def unlock_vault(self, password: str) -> bytes:
        """Unlock existing vault and return KEK"""
        print(" Attempting to unlock vault...")
        
        key_file = self.vault_path / "master_key.enc"
        if not key_file.exists():
            raise FileNotFoundError(" No vault found!")
        
        # Load encrypted data
        with open(key_file, 'rb') as f:
            data = f.read()
        
        # Extract salt and encrypted KEK
        salt = data[:32]  # First 32 bytes
        encrypted_kek = data[32:]
        
        # Derive master key from password
        master_key, _ = self.crypto.derive_key(password, salt)
        
        # Decrypt KEK
        print("   KEK decrypted successfully")
        kek = self.crypto.decrypt_data(encrypted_kek, master_key)
        
        print(" Vault unlocked successfully!")
        return kek
    
    def save_metadata(self, metadata: dict, kek: bytes) -> bool:
        """Save vault metadata encrypted with KEK"""
        try:
            # Convert to JSON
            metadata_json = json.dumps(metadata).encode()
            
            # Encrypt with KEK
            encrypted = self.crypto.encrypt_data(metadata_json, kek)
            
            # Save to file
            with open(self.vault_path / "metadata.enc", 'wb') as f:
                f.write(encrypted)
            
            return True
        except Exception as e:
            print(f" Error saving metadata: {e}")
            return False
    
    def load_metadata(self, kek: bytes) -> dict:
        """Load and decrypt vault metadata"""
        metadata_path = self.vault_path / "metadata.enc"
        
        # DEBUG: Add this
        print(f" DEBUG: Loading metadata from {metadata_path}")
        
        if not metadata_path.exists():
            print(" DEBUG: No metadata file, returning empty dict")
            return {}
        
        try:
            # Read encrypted data
            with open(metadata_path, 'rb') as f:
                encrypted_data = f.read()
            
            # DEBUG: Show what we're reading
            print(f"  DEBUG: Metadata file size: {len(encrypted_data)} bytes")
            print(f"  DEBUG: First 20 bytes: {encrypted_data[:20].hex()}")
            
            # Try to decrypt
            print(f"  DEBUG: Attempting decryption with {len(kek)} byte key")
            decrypted_data = self.crypto.decrypt_data(encrypted_data, kek)
            
            # Parse JSON
            metadata = json.loads(decrypted_data.decode())
            
            print(f"  DEBUG: Successfully loaded {len(metadata)} file entries")
            return metadata
            
        except Exception as e:
            print(f"  DEBUG ERROR: {e}")
            print(f"  DEBUG: Returning empty metadata due to error")
            return {}

# Test function
def test_key_manager():
    """Test the key manager"""
    print(" Testing Key Manager...")
    
    # Create test vault
    test_path = "./test_vault_keys"
    km = KeyManager(test_path)
    
    # Create vault
    password = "test123"
    km.initialize_vault(password)
    
    # Unlock vault
    kek = km.unlock_vault(password)
    print(f"KEK: {kek[:8].hex()}...")
    
    # Test metadata
    test_metadata = {"file1": {"name": "test.txt", "size": 100}}
    km.save_metadata(test_metadata, kek)
    
    loaded = km.load_metadata(kek)
    print(f"Loaded metadata: {loaded}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_path, ignore_errors=True)
    
    print("------- Key Manager test completed")

if __name__ == "__main__":
    test_key_manager()
