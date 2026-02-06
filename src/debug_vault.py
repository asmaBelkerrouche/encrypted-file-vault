# debug_vault.py
import sys
import os
import json
import base64
sys.path.insert(0, '.')

print(" DEBUG VAULT PASSWORD ISSUE")
print("=" * 70)

from src.auth.key_manager import KeyManager
from src.crypto.engine import CryptoEngine

# Clean any existing vault
test_path = "./debug_vault"
import shutil
if os.path.exists(test_path):
    shutil.rmtree(test_path)

print("1. Creating new vault with password 'test123'...")
km = KeyManager(test_path)
success = km.initialize_vault("test123")
print(f"   Success: {success}")

print("\n2. Checking what's in the key file...")
key_file = os.path.join(test_path, "master_key.enc")
if os.path.exists(key_file):
    with open(key_file, 'r') as f:
        key_data = json.load(f)
    
    print(f"   File exists: ✓")
    print(f"   Salt length: {len(key_data['salt'])} chars")
    print(f"   Encrypted KEK length: {len(key_data['encrypted_kek'])} chars")
    print(f"   Encrypted Master Key length: {len(key_data['encrypted_master_key'])} chars")
else:
    print("    Key file not created!")

print("\n3. Trying to unlock...")
km2 = KeyManager(test_path)
try:
    master_key = km2.unlock_vault("test123")
    print(f"    SUCCESS! Master key: {master_key[:8].hex()}...")
    print(f"   Key length: {len(master_key)} bytes (should be 32)")
except Exception as e:
    print(f"    FAILED: {e}")
    print(f"   Error type: {type(e).__name__}")

print("\n4. Manual verification...")
engine = CryptoEngine()

# Extract components
salt = base64.b64decode(key_data["salt"])
encrypted_kek = base64.b64decode(key_data["encrypted_kek"])
encrypted_master = base64.b64decode(key_data["encrypted_master_key"])

print(f"   Salt bytes: {salt[:8].hex()}...")
print(f"   Encrypted KEK bytes: {encrypted_kek[:8].hex()}...")
print(f"   Encrypted Master bytes: {encrypted_master[:8].hex()}...")

# Try to derive storage key
print("\n   Trying to derive storage key from 'test123'...")
storage_key, derived_salt = engine.derive_key("test123", salt)
print(f"   Storage key: {storage_key[:8].hex()}...")
print(f"   Derived salt matches: {derived_salt == salt}")

# Try wrong password
print("\n   Trying wrong password 'wrong'...")
wrong_storage_key, _ = engine.derive_key("wrong", salt)
print(f"   Wrong storage key: {wrong_storage_key[:8].hex()}...")
print(f"   Keys match? {storage_key[:8].hex() == wrong_storage_key[:8].hex()}")

# Clean up
if os.path.exists(test_path):
    shutil.rmtree(test_path)

print("\n" + "=" * 70)