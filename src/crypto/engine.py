# src/crypto/engine.py
"""
Encryption/Decryption Engine - Core of the vault
"""

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

class CryptoEngine:
    def __init__(self):
        print(" Crypto Engine Initialized")
        self.iv_size = 16  # AES block size
        self.key_size = 32  # AES-256 = 32 bytes
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Convert password to strong encryption key"""
        if salt is None:
            salt = get_random_bytes(32)
        
        # PBKDF2 makes passwords resistant to brute-force attacks
        key = PBKDF2(password.encode(), salt, 
                    dkLen=self.key_size,
                    count=100000)  # Makes it slow to attack
        
        return key, salt
    
    def encrypt_data(self, plain_data: bytes, key: bytes) -> bytes:
        """Encrypt data with AES-256"""
        # Generate random IV
        iv = get_random_bytes(self.iv_size)
        
        # Create AES cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Add padding
        pad_length = 16 - (len(plain_data) % 16)
        plain_data += bytes([pad_length]) * pad_length
        
        # Encrypt
        encrypted = cipher.encrypt(plain_data)
        
        # Return IV + encrypted data
        return iv + encrypted
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data with AES-256"""
        # Extract IV (first 16 bytes)
        iv = encrypted_data[:self.iv_size]
        actual_encrypted = encrypted_data[self.iv_size:]
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt
        decrypted = cipher.decrypt(actual_encrypted)
        
        # Remove padding
        pad_length = decrypted[-1]
        return decrypted[:-pad_length]
    
    def generate_file_key(self) -> bytes:
        """Generate random key for file encryption"""
        return get_random_bytes(self.key_size)
    
    def test_encryption(self):
        """Simple test to verify crypto works"""
        print(" Testing encryption...")
        
        # Create a test key
        test_password = "test123"
        key, salt = self.derive_key(test_password)
        
        # Test data
        test_data = b"Hello, Encrypted World!"
        
        # Encrypt
        encrypted = self.encrypt_data(test_data, key)
        print(f"   Original: {test_data}")
        print(f"   Encrypted: {encrypted[:20]}...")
        
        # Decrypt
        decrypted = self.decrypt_data(encrypted, key)
        print(f"   Decrypted: {decrypted}")
        
        if test_data == decrypted:
            print(" Encryption test PASSED!")
            return True
        else:
            print(" Encryption test FAILED!")
            return False

# Quick test if run directly
if __name__ == "__main__":
    engine = CryptoEngine()
    engine.test_encryption()