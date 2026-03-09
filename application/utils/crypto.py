from cryptography.fernet import Fernet, InvalidToken
import config
import os
import stat

def get_or_create_encryption_key():
    """
    Get encryption key from file or create new one
    Ensures key persists across restarts
    """
    key_file = config.ENCRYPTION_KEY_FILE
    
    if key_file.exists():
        # Load existing key
        with open(key_file, 'rb') as f:
            key = f.read()
        return key
    else:
        # Generate new key
        key = Fernet.generate_key()
        
        # Ensure directory exists
        os.makedirs(key_file.parent, exist_ok=True)
        
        # Save key
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Set restrictive permissions (owner read/write only)
        try:
            os.chmod(key_file, stat.S_IRUSR | stat.S_IWUSR)
        except:
            pass  # Windows doesn't support chmod
        
        return key

# Initialize encryption key at module load
ENCRYPTION_KEY = get_or_create_encryption_key()
_cipher = Fernet(ENCRYPTION_KEY)

def encrypt_api_key(api_key):
    """
    Encrypt API key for storage
    
    Args:
        api_key: Plain text API key
    
    Returns:
        Encrypted API key as string
    """
    if not api_key:
        return None
    
    try:
        encrypted = _cipher.encrypt(api_key.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_api_key(encrypted_key):
    """
    Decrypt stored API key
    
    Args:
        encrypted_key: Encrypted API key string
    
    Returns:
        Decrypted API key or None if failed
    """
    if not encrypted_key:
        return None
    
    try:
        decrypted = _cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except InvalidToken:
        print("Failed to decrypt API key - encryption key may have changed")
        return None
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
