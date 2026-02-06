# src/storage/file_manager.py - FIXED VERSION
"""
File Storage Manager - Handles actual file encryption/decryption
FIXED: File ID generation for Windows compatibility
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from src.crypto.engine import CryptoEngine

class FileManager:
    def __init__(self, vault_path: str = "./vault_data"):
        """
        Initialize file manager
        vault_path: Where encrypted files will be stored
        """
        self.vault_path = Path(vault_path)
        self.files_path = self.vault_path / "encrypted_files"
        self.files_path.mkdir(exist_ok=True)  # Create folder if doesn't exist
        self.crypto = CryptoEngine()
        print(" File Manager Initialized")
    
    def _generate_file_id(self) -> str:
        """Generate safe filename-friendly ID (Windows compatible)"""
        # Get random bytes and convert to hex (safe for all OS)
        random_bytes = self.crypto.generate_file_key()[:8]  # 8 bytes = 16 hex chars
        return random_bytes.hex()  # Returns something like "a1b2c3d4e5f67890"
    
    def add_file(self, source_path: str, master_key: bytes) -> dict:
        """
        Add a file to the encrypted vault
        """
        source = Path(source_path)
        
        # Check if file exists
        if not source.exists():
            raise FileNotFoundError(f" File not found: {source_path}")
        
        print(f"\n Adding: {source.name} ({source.stat().st_size:,} bytes)")
        
        # FIXED: Generate safe file ID
        file_id = self._generate_file_id()
        
        # Generate unique key for this specific file
        file_key = self.crypto.generate_file_key()
        
        # Encrypt the file key with master key
        encrypted_file_key = self.crypto.encrypt_data(file_key, master_key)
        
        # Read the actual file content
        with open(source_path, 'rb') as f:
            file_data = f.read()
        
        # Calculate hash for integrity checking
        file_hash = hashlib.sha256(file_data).hexdigest()[:16]
        
        # Encrypt the file content with the file's unique key
        print("   Encrypting...")
        encrypted_data = self.crypto.encrypt_data(file_data, file_key)
        
        # Save the encrypted file
        encrypted_filename = f"{file_id}.enc"
        encrypted_path = self.files_path / encrypted_filename
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Create metadata
        metadata = {
            "file_id": file_id,
            "original_name": source.name,
            "original_path": str(source.parent),
            "original_size": source.stat().st_size,
            "encrypted_size": len(encrypted_data),
            "created_at": datetime.now().isoformat(),
            "encrypted_key": base64.b64encode(encrypted_file_key).decode(),
            "file_type": source.suffix.lower(),
            "hash": file_hash,
            "chunks": 1
        }
        
        print(f" Added! File ID: {file_id}")
        print(f"   Original: {metadata['original_size']:,} bytes")
        print(f"   Encrypted: {metadata['encrypted_size']:,} bytes")
        
        return metadata
    
    def get_file(self, file_id: str, master_key: bytes, metadata: dict) -> bytes:
        """
        Retrieve a file from the vault
        """
        encrypted_path = self.files_path / f"{file_id}.enc"
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f" Encrypted file not found: {file_id}")
        
        print(f"\n📥 Retrieving: {metadata.get('original_name', 'Unknown')}")
        
        # Load the encrypted file from disk
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the file key using master key
        encrypted_key = base64.b64decode(metadata["encrypted_key"])
        file_key = self.crypto.decrypt_data(encrypted_key, master_key)
        
        # Decrypt the actual file content
        print("   Decrypting...")
        decrypted_data = self.crypto.decrypt_data(encrypted_data, file_key)
        
        # Verify size matches
        if len(decrypted_data) != metadata["original_size"]:
            print(f"  Warning: Size mismatch!")
            print(f"   Expected: {metadata['original_size']:,} bytes")
            print(f"   Got: {len(decrypted_data):,} bytes")
        
        # Optional: Verify hash
        if "hash" in metadata:
            current_hash = hashlib.sha256(decrypted_data).hexdigest()[:16]
            if current_hash != metadata["hash"]:
                print("  Warning: File hash doesn't match!")
            else:
                print(" Integrity check passed")
        
        print(f" Retrieved! Size: {len(decrypted_data):,} bytes")
        return decrypted_data
    
    def delete_file(self, file_id: str, secure_wipe: bool = False):
        """
        Delete a file from the vault
        """
        file_path = self.files_path / f"{file_id}.enc"
        
        if not file_path.exists():
            print(f"  File {file_id} not found")
            return
        
        if secure_wipe:
            print(f" Secure deleting {file_id}...")
            # Overwrite file 3 times with random data
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                for i in range(3):
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
        else:
            print(f"  Deleting {file_id}...")
        
        # Actually delete the file
        file_path.unlink()
        print(f" Deleted")
    
    def get_vault_stats(self) -> dict:
        """Get statistics about files in the vault"""
        encrypted_files = list(self.files_path.glob("*.enc"))
        
        total_size = 0
        for f in encrypted_files:
            total_size += f.stat().st_size
        
        return {
            "total_files": len(encrypted_files),
            "total_size": total_size,
            "vault_path": str(self.files_path)
        }
    
    def list_encrypted_files(self) -> list:
        """List all encrypted files in the vault"""
        files = []
        for f in self.files_path.glob("*.enc"):
            files.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return files

# Simple test
if __name__ == "__main__":
    print(" Quick test of File Manager...")
    fm = FileManager("./test_vault")
    print(f"Generated file ID example: {fm._generate_file_id()}")