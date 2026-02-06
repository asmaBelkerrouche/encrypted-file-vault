# src/main_fixed.py - SIMPLE WORKING VERSION
import os
import sys
import getpass
from pathlib import Path

# Fix imports
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.auth.key_manager import KeyManager
from src.storage.file_manager import FileManager
from src.crypto.engine import CryptoEngine

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print("=" * 60)
    print(" ENCRYPTED FILE VAULT SYSTEM")
    print("=" * 60)
    print(f" {title}")
    print("-" * 60)

def main():
    while True:
        print_header("MAIN MENU")
        
        # Always use explicit path
        vault_path = "./vault_data"
        key_file = os.path.join(vault_path, "master_key.enc")
        
        print(f"Vault location: {os.path.abspath(vault_path)}")
        print(f"Vault exists: {os.path.exists(key_file)}")
        
        if os.path.exists(key_file):
            print("\n1. Unlock vault")
            print("2. Delete and create new vault")
            print("3. Exit")
            
            choice = input("\nSelect: ")
            
            if choice == "1":
                unlock_vault()
            elif choice == "2":
                confirm = input("Delete existing vault? (y/N): ")
                if confirm.lower() == 'y':
                    import shutil
                    shutil.rmtree(vault_path, ignore_errors=True)
                    create_vault()
            elif choice == "3":
                print("\nGoodbye!")
                break
        else:
            print("\n1. Create new vault")
            print("2. Exit")
            
            choice = input("\nSelect: ")
            
            if choice == "1":
                create_vault()
            elif choice == "2":
                print("\nGoodbye!")
                break

def create_vault():
    print_header("CREATE VAULT")
    
    print("IMPORTANT: You will create a NEW vault")
    print("Remember your password - it cannot be recovered!\n")
    
    while True:
        password = getpass.getpass("Set password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print(" Passwords don't match!\n")
            continue
        
        if len(password) < 4:
            print("  Password is very short (minimum recommended: 8)\n")
            continue
        
        # Create vault
        try:
            km = KeyManager("./vault_data")  # EXPLICIT PATH
            if km.initialize_vault(password):
                print(f"\n Vault created!")
                print(f" Password: {password}")
                print(f" Location: {os.path.abspath('./vault_data')}")
                input("\nPress Enter to continue...")
                return
        except Exception as e:
            print(f" Error: {e}")
            return

def unlock_vault():
    print_header("UNLOCK VAULT")
    
    vault_path = "./vault_data"
    key_file = os.path.join(vault_path, "master_key.enc")
    
    if not os.path.exists(key_file):
        print(" No vault found!")
        input("\nPress Enter to continue...")
        return
    
    print(f"Vault found at: {os.path.abspath(vault_path)}")
    print("\nCommon passwords to try: 123, password, test123")
    
    attempts = 3
    while attempts > 0:
        password = getpass.getpass(f"\nPassword ({attempts} attempts): ")
        
        print(f"You entered: {'*' * len(password)}")
        
        try:
            # Use EXPLICIT path
            km = KeyManager("./vault_data")
            master_key = km.unlock_vault(password)
            print(f"\n SUCCESS! Unlocked.")
            print(f"Master key: {master_key[:8].hex()}...")
            vault_menu(km, master_key)
            return
        except Exception as e:
            attempts -= 1
            print(f" Failed: {e}")
            if attempts > 0:
                print(f"{attempts} attempts remaining")
            else:
                print(" Too many failed attempts")
    
    input("\nPress Enter to continue...")

def vault_menu(key_manager, master_key):
    file_manager = FileManager("./vault_data")
    
    while True:
        print_header("VAULT UNLOCKED")
        
        print("1. Add file")
        print("2. List files")
        print("3. Extract file")
        print("4. Test encryption")
        print("5. Lock vault")
        
        choice = input("\nSelect: ")
        
        if choice == "1":
            add_file(file_manager, master_key, key_manager)
        elif choice == "2":
            list_files(key_manager, master_key)
        elif choice == "3":
            extract_file(file_manager, master_key, key_manager)
        elif choice == "4":
            test_encryption()
        elif choice == "5":
            print("\n Locking vault...")
            return

def add_file(fm, master_key, km):
    print_header("ADD FILE")
    
    path = input("File path: ").strip()
    
    if not os.path.exists(path):
        print(" File not found")
        input("\nPress Enter...")
        return
    
    try:
        metadata = fm.add_file(path, master_key)
        
        # Update vault metadata
        existing = km.load_metadata(master_key)
        existing[metadata["file_id"]] = metadata
        km.save_metadata(existing, master_key)
        
        print(f" Added! ID: {metadata['file_id']}")
    except Exception as e:
        print(f" Error: {e}")
    
    input("\nPress Enter...")

def list_files(km, master_key):
    print_header("FILES")
    
    metadata = km.load_metadata(master_key)
    
    if not metadata:
        print("No files in vault")
    else:
        for file_id, info in metadata.items():
            print(f" {info['original_name']}")
            print(f"   ID: {file_id}")
            print(f"   Size: {info['original_size']:,} bytes")
            print()
    
    input("\nPress Enter...")

def extract_file(fm, master_key, km):
    metadata = km.load_metadata(master_key)
    
    if not metadata:
        print("No files to extract")
        input("\nPress Enter...")
        return
    
    print_header("EXTRACT FILE")
    
    files = list(metadata.items())
    for i, (file_id, info) in enumerate(files, 1):
        print(f"{i}. {info['original_name']}")
    
    try:
        choice = input("\nSelect (number): ")
        idx = int(choice) - 1
        
        if 0 <= idx < len(files):
            file_id, info = files[idx]
            
            output = input(f"Output [{info['original_name']}]: ").strip()
            if not output:
                output = info['original_name']
            
            data = fm.get_file(file_id, master_key, info)
            
            with open(output, 'wb') as f:
                f.write(data)
            
            print(f"  Saved to: {output}")
    except Exception as e:
        print(f" Error: {e}")
    
    input("\nPress Enter...")

def test_encryption():
    print_header("TEST")
    
    engine = CryptoEngine()
    engine.test_encryption()
    
    input("\nPress Enter...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n Error: {e}")
        input("Press Enter to exit...")