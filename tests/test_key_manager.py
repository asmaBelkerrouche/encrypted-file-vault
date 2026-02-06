# test_key_manager.py (Save in encrypted-vault folder)

"""
Test the Key Manager
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.auth.key_manager import KeyManager

def test_key_manager():
    print("🧪 Testing Key Manager...")
    print("-" * 40)
    
    # Create a test vault
    km = KeyManager("./test_vault")
    
    # Test 1: Initialize new vault
    print("Test 1: Initialize vault")
    success = km.initialize_vault("MyStrongPassword123!")
    print(f"Initialization: {'   PASS' if success else '    FAIL'}")
    
    # Test 2: Check vault exists
    print(f"\nTest 2: Vault exists check")
    exists = km.vault_exists()
    print(f"Vault exists: {'   YES' if exists else '    NO'}")
    
    # Test 3: Unlock with correct password
    print("\nTest 3: Unlock with correct password")
    try:
        master_key = km.unlock_vault("MyStrongPassword123!")
        print(f"Unlock successful:    YES")
        print(f"Master key length: {len(master_key)} bytes")
    except Exception as e:
        print(f"Unlock failed:     {e}")
    
    # Test 4: Unlock with wrong password
    print("\nTest 4: Unlock with wrong password")
    try:
        km.unlock_vault("WrongPassword")
        print("    FAIL: Should have rejected wrong password")
    except Exception as e:
        print(f"   PASS: Correctly rejected - {e}")
    
    # Test 5: Save and load metadata
    print("\nTest 5: Metadata operations")
    test_metadata = {
        "files": ["secret.txt", "photo.jpg"],
        "count": 2,
        "created": "2024-01-01"
    }
    
    km.save_metadata(test_metadata, master_key)
    loaded = km.load_metadata(master_key)
    
    if loaded == test_metadata:
        print("   Metadata save/load: PASS")
    else:
        print("    Metadata save/load: FAIL")
        print(f"Expected: {test_metadata}")
        print(f"Got: {loaded}")
    
    print("\n" + "=" * 40)
    print("------ All tests completed!")
    
    # Cleanup
    import shutil
    shutil.rmtree("./test_vault", ignore_errors=True)

if __name__ == "__main__":
    test_key_manager()