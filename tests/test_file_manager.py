# tests/test_file_manager.py - FIXED
"""
Test the File Manager with actual files - FIXED VERSION
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(" TESTING FILE MANAGER (FIXED VERSION)")
print("=" * 60)

try:
    from src.auth.key_manager import KeyManager
    from src.storage.file_manager import FileManager
    
    # Setup
    test_vault = "./test_vault_day3_fixed"
    
    # Clean up old test vault
    import shutil
    if os.path.exists(test_vault):
        shutil.rmtree(test_vault)
    
    print("1.  Creating vault and unlocking...")
    km = KeyManager(test_vault)
    km.initialize_vault("MyPassword123!")
    
    km2 = KeyManager(test_vault)
    master_key = km2.unlock_vault("MyPassword123!")
    
    print("\n2.  Creating File Manager...")
    fm = FileManager(test_vault)
    
    # Create a test file
    print("\n3.  Creating test files...")
    
    # File 1: Text file
    text_file = "secret_document.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("TOP SECRET DOCUMENT\n")
        f.write("=" * 40 + "\n")
        f.write("1. Launch codes: 1234-5678-9012\n")
        f.write("2. Bitcoin wallet: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n")
        f.write("3. Password: hunter2\n")
        f.write("\nEnd of document.\n")
    
    # File 2: Another file
    another_file = "notes.md"
    with open(another_file, 'w') as f:
        f.write("# My Private Notes\n")
        f.write("- Buy milk\n")
        f.write("- Learn encryption\n")
        f.write("- Backup important files\n")
    
    print(f"   Created: {text_file}, {another_file}")
    
    # Test 1: Add files to vault
    print("\n4.  Adding files to vault...")
    metadata1 = fm.add_file(text_file, master_key)
    metadata2 = fm.add_file(another_file, master_key)
    
    print(f"   File 1 ID: {metadata1['file_id']}")
    print(f"   File 2 ID: {metadata2['file_id']}")
    
    # Test 2: List files
    print("\n5.  Listing vault contents...")
    stats = fm.get_vault_stats()
    print(f"   Total files: {stats['total_files']}")
    print(f"   Total size: {stats['total_size']:,} bytes")
    
    files = fm.list_encrypted_files()
    for f in files:
        print(f"   - {f['filename']} ({f['size']:,} bytes)")
    
    # Test 3: Retrieve a file
    print("\n6.  Retrieving file from vault...")
    print(f"   Getting: {metadata1['original_name']}")
    decrypted_data = fm.get_file(metadata1['file_id'], master_key, metadata1)
    
    # Save to new file
    output_file = "retrieved_document.txt"
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"   Saved as: {output_file}")
    
    # Show preview
    preview = decrypted_data[:100].decode('utf-8', errors='ignore')
    print(f"   Preview: {preview}...")
    
    # Verify it matches original
    with open(text_file, 'rb') as f:
        original = f.read()
    
    if original == decrypted_data:
        print("    Perfect match with original!")
    else:
        print("    Content doesn't match!")
    
    # Test 4: Delete a file
    print("\n7.  Testing delete...")
    fm.delete_file(metadata2['file_id'], secure_wipe=False)
    
    # Check vault after deletion
    stats_after = fm.get_vault_stats()
    print(f"   Files after deletion: {stats_after['total_files']}")
    
    # Test 5: Try to get deleted file (should fail)
    print("\n8.  Testing error handling...")
    try:
        fm.get_file(metadata2['file_id'], master_key, metadata2)
        print("    Should have failed!")
    except FileNotFoundError:
        print("    Correctly failed - file not found")
    
    # Final stats
    print("\n9.  Final vault status:")
    final_stats = fm.get_vault_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    # Cleanup
    print("\n10.  Cleaning up...")
    files_to_clean = [text_file, another_file, output_file]
    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)
            print(f"   Deleted: {f}")
    
    if os.path.exists(test_vault):
        shutil.rmtree(test_vault)
        print(f"   Deleted: {test_vault}")
    
    print("\n" + "=" * 60)
    print("🎉 FILE MANAGER TESTS COMPLETED SUCCESSFULLY!")
    
except Exception as e:
    print(f"\n ERROR: {e}")
    import traceback
    traceback.print_exc()
    
    # Cleanup on error
    files_to_clean = ["secret_document.txt", "notes.md", "retrieved_document.txt"]
    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)
    
    if os.path.exists("./test_vault_day3_fixed"):
        import shutil
        shutil.rmtree("./test_vault_day3_fixed")