# debug_password.py
import sys
import os
sys.path.insert(0, '.')

from src.auth.key_manager import KeyManager

print(" DEBUGGING PASSWORD ISSUE")
print("=" * 60)

# Clean any existing test vault
import shutil
if os.path.exists("./debug_vault"):
    shutil.rmtree("./debug_vault")

print("1. Creating vault with password 'test123'...")
km1 = KeyManager("./debug_vault")
success = km1.initialize_vault("test123")
print(f"   Created: {success}")

print("\n2. Trying to unlock with SAME instance...")
try:
    master_key = km1.unlock_vault("test123")
    print(f"    SUCCESS with same instance!")
    print(f"   Master key: {master_key[:8].hex()}...")
except Exception as e:
    print(f"    FAILED with same instance: {e}")

print("\n3. Trying to unlock with NEW instance...")
km2 = KeyManager("./debug_vault")
try:
    master_key = km2.unlock_vault("test123")
    print(f"    SUCCESS with new instance!")
    print(f"   Master key: {master_key[:8].hex()}...")
except Exception as e:
    print(f"    FAILED with new instance: {e}")

print("\n4. Trying WRONG password...")
try:
    km2.unlock_vault("wrongpassword")
    print("    SHOULD HAVE FAILED but didn't!")
except Exception as e:
    print(f"    Correctly failed: {e}")

# Cleanup
if os.path.exists("./debug_vault"):
    shutil.rmtree("./debug_vault")

print("\n" + "=" * 60)
print("Debug complete!")