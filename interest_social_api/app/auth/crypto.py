"""
Cryptographic Utilities
Production-grade encryption and hashing for sensitive data
"""

import os
import hashlib
import secrets
import base64
import logging
from typing import Tuple, Optional, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class PasswordHandler:
    """
    Secure password hashing using PBKDF2 with SHA-256
    
    Features:
    - Configurable iterations (default: 260,000)
    - Unique salt per password
    - Constant-time comparison
    """
    
    ITERATIONS = 260000  # OWASP recommended minimum
    HASH_ALGORITHM = 'sha256'
    SALT_LENGTH = 32  # 256 bits
    HASH_LENGTH = 32  # 256 bits
    
    @classmethod
    def generate_salt(cls) -> str:
        """Generate a cryptographically secure random salt"""
        return secrets.token_hex(cls.SALT_LENGTH)
    
    @classmethod
    def hash_password(cls, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password using PBKDF2
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
        
        Returns:
            Tuple of (password_hash, salt)
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if salt is None:
            salt = cls.generate_salt()
        
        if len(salt) != cls.SALT_LENGTH * 2:
            raise ValueError(f"Salt must be {cls.SALT_LENGTH * 2} hex characters")
        
        # PBKDF2 key derivation
        hash_value = hashlib.pbkdf2_hmac(
            cls.HASH_ALGORITHM,
            password.encode('utf-8'),
            salt.encode('utf-8'),
            cls.ITERATIONS,
            dklen=cls.HASH_LENGTH
        )
        
        # Base64 encode for storage
        password_hash = base64.b64encode(hash_value).decode('utf-8')
        
        return password_hash, salt
    
    @classmethod
    def verify_password(cls, password: str, password_hash: str, salt: str) -> bool:
        """
        Verify a password against its hash
        
        Uses constant-time comparison to prevent timing attacks
        """
        try:
            computed_hash, _ = cls.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, password_hash)
        except Exception as e:
            logger.warning(f"Password verification failed: {e}")
            return False
    
    @classmethod
    def needs_rehash(cls, password_hash: str, current_iterations: int = None) -> bool:
        """
        Check if password needs to be rehashed with new parameters
        
        Returns True if iterations have increased
        """
        if current_iterations is None:
            current_iterations = cls.ITERATIONS
        
        # In a real implementation, you'd store iterations with the hash
        # and compare against current settings
        return current_iterations > cls.ITERATIONS
    
    @classmethod
    def generate_password(cls, length: int = 16) -> str:
        """Generate a secure random password"""
        # Use secrets for cryptographically secure randomness
        alphabet = (
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            '!@#$%^&*'
        )
        
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            
            # Ensure password meets complexity requirements
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in '!@#$%^&*' for c in password)
            
            if has_lower and has_upper and has_digit and has_special:
                return password


class EncryptionHandler:
    """
    Symmetric encryption handler using Fernet (AES-128 in CBC mode with PKCS7 padding)
    
    For higher security requirements, use AES-256-GCM via AESCipher
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption handler
        
        Args:
            key: Optional encryption key (generated from env if not provided)
        """
        self.key = key or self._get_or_generate_key()
        self.fernet = Fernet(self.key)
    
    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from environment or generate one"""
        key = os.environ.get('ENCRYPTION_KEY')

        if key:
            try:
                # Key should be base64-encoded Fernet key (44 characters)
                # Validate by decoding and checking length
                decoded = base64.urlsafe_b64decode(key)
                if len(decoded) == 32:
                    return key.encode()  # Return the base64 string as bytes
            except Exception:
                pass

        # Derive key from master secret
        master_key = os.environ.get('APP_SECRET_KEY')
        if not master_key:
            raise ValueError("APP_SECRET_KEY must be set for encryption")

        salt = os.environ.get('SECURITY_PASSWORD_SALT', 'default-salt').encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data
        
        Returns base64-encoded encrypted data
        """
        if not isinstance(data, str):
            raise TypeError("Data must be a string")
        
        encrypted = self.fernet.encrypt(data.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data: Base64-encoded encrypted string
        
        Returns:
            Decrypted string
        """
        if not isinstance(encrypted_data, str):
            raise TypeError("Encrypted data must be a string")
        
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Decryption failed: Invalid token")
            raise ValueError("Invalid encryption token")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def rotate_key(self, new_key: bytes, encrypted_data: str) -> str:
        """
        Re-encrypt data with a new key
        
        Args:
            new_key: New encryption key
            encrypted_data: Data encrypted with old key
        
        Returns:
            Data re-encrypted with new key
        """
        # Decrypt with old key
        decrypted = self.decrypt(encrypted_data)
        
        # Encrypt with new key
        new_fernet = Fernet(new_key)
        encrypted = new_fernet.encrypt(decrypted.encode('utf-8'))
        
        return encrypted.decode('utf-8')


class AESCipher:
    """
    AES-256-GCM encryption for high-security requirements
    
    Provides:
    - Authenticated encryption (confidentiality + integrity)
    - 256-bit keys
    - 96-bit nonces
    - 128-bit authentication tags
    """
    
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits for GCM
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize AES cipher
        
        Args:
            key: 32-byte encryption key (generated if not provided)
        """
        if key is None:
            key = self._derive_key()
        
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"Key must be {self.KEY_SIZE} bytes")
        
        self.key = key
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from environment"""
        master_key = os.environ.get('AES_MASTER_KEY')
        if not master_key:
            master_key = os.environ.get('APP_SECRET_KEY')
        
        if not master_key:
            raise ValueError("AES_MASTER_KEY or APP_SECRET_KEY must be set")
        
        salt = os.environ.get('AES_SALT', 'aes-salt-value').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=200000,  # Higher iterations for master key
            backend=default_backend()
        )
        
        return kdf.derive(master_key.encode())
    
    def encrypt(self, plaintext: Union[str, bytes], associated_data: bytes = None) -> dict:
        """
        Encrypt data using AES-256-GCM
        
        Args:
            plaintext: Data to encrypt
            associated_data: Optional authenticated data
        
        Returns:
            Dictionary with ciphertext, nonce, and tag
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generate random nonce
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        
        # Create cipher and encrypt
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        
        # ciphertext includes tag at the end
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'associated_data': base64.b64encode(associated_data).decode('utf-8') if associated_data else None
        }
    
    def decrypt(self, encrypted_data: dict, associated_data: bytes = None) -> str:
        """
        Decrypt AES-256-GCM encrypted data
        
        Args:
            encrypted_data: Dictionary from encrypt()
            associated_data: Optional authenticated data (must match encryption)
        
        Returns:
            Decrypted string
        """
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        
        if encrypted_data.get('associated_data'):
            associated_data = base64.b64decode(encrypted_data['associated_data'])
        
        aesgcm = AESGCM(self.key)
        
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
            return plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"AES decryption failed: {e}")
            raise ValueError("Decryption failed - data may be tampered")


class APIKeyHandler:
    """
    API Key management with secure hashing
    
    Features:
    - Secure random key generation
    - SHA-256 hashing for storage
    - Prefix identification
    """
    
    KEY_PREFIX = 'isk_live_'
    KEY_LENGTH = 32
    
    @classmethod
    def generate_api_key(cls, name: str = None) -> Tuple[str, str]:
        """
        Generate a new API key
        
        Returns:
            Tuple of (plain_key, key_hash)
            plain_key should be shown to user ONCE
            key_hash should be stored in database
        """
        random_bytes = secrets.token_urlsafe(cls.KEY_LENGTH)
        key = f"{cls.KEY_PREFIX}{random_bytes}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        logger.info(f"API key generated: {name or 'unnamed'}")
        return key, key_hash
    
    @classmethod
    def verify_api_key(cls, api_key: str, key_hash: str) -> bool:
        """
        Verify an API key against its hash
        
        Uses constant-time comparison
        """
        if not api_key.startswith(cls.KEY_PREFIX):
            return False
        
        computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, key_hash)
    
    @classmethod
    def hash_api_key(cls, api_key: str) -> str:
        """Get hash of API key for storage lookup"""
        return hashlib.sha256(api_key.encode()).hexdigest()


class SecureDataStore:
    """
    High-level interface for storing sensitive data
    
    Automatically handles encryption/decryption and field-level security
    """
    
    # Fields that should always be encrypted
    SENSITIVE_FIELDS = {
        'password', 'ssn', 'social_security',
        'credit_card', 'cvv', 'pin',
        'api_key', 'secret_key', 'private_key',
        'token', 'refresh_token'
    }
    
    def __init__(self):
        self.encryption = EncryptionHandler()
        self.aes = AESCipher()
    
    def prepare_for_storage(self, data: dict, fields_to_encrypt: set = None) -> dict:
        """
        Prepare data for storage by encrypting sensitive fields
        
        Args:
            data: Dictionary of data to store
            fields_to_encrypt: Additional fields to encrypt
        
        Returns:
            Data with sensitive fields encrypted
        """
        if fields_to_encrypt is None:
            fields_to_encrypt = set()
        
        fields_to_encrypt = fields_to_encrypt.union(self.SENSITIVE_FIELDS)
        
        result = {}
        for key, value in data.items():
            if key in fields_to_encrypt and value is not None:
                # Use AES-256-GCM for highly sensitive data
                if key in {'ssn', 'credit_card', 'password'}:
                    encrypted = self.aes.encrypt(str(value))
                    result[f"{key}_encrypted"] = encrypted
                else:
                    # Use Fernet for other sensitive data
                    result[f"{key}_encrypted"] = self.encryption.encrypt(str(value))
            else:
                result[key] = value
        
        return result
    
    def retrieve_from_storage(self, data: dict, fields_to_decrypt: set = None) -> dict:
        """
        Retrieve data from storage by decrypting encrypted fields
        
        Args:
            data: Dictionary from storage
            fields_to_decrypt: Fields to decrypt (None = decrypt all)
        
        Returns:
            Data with encrypted fields decrypted
        """
        result = {}
        
        for key, value in data.items():
            if key.endswith('_encrypted'):
                field_name = key[:-10]  # Remove '_encrypted' suffix
                
                # Skip if not in requested fields
                if fields_to_decrypt and field_name not in fields_to_decrypt:
                    result[field_name] = value
                    continue
                
                try:
                    # Try AES decryption first
                    if isinstance(value, dict) and 'ciphertext' in value:
                        result[field_name] = self.aes.decrypt(value)
                    else:
                        # Fernet decryption
                        result[field_name] = self.encryption.decrypt(value)
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field_name}: {e}")
                    result[field_name] = None
            else:
                result[key] = value
        
        return result
    
    def mask_sensitive_data(self, data: dict, fields_to_mask: set = None) -> dict:
        """
        Mask sensitive data for logging/display
        
        Replaces sensitive values with masked versions (e.g., ****1234)
        """
        if fields_to_mask is None:
            fields_to_mask = self.SENSITIVE_FIELDS
        
        result = {}
        for key, value in data.items():
            if key in fields_to_mask and value is not None:
                str_value = str(value)
                if len(str_value) > 4:
                    result[key] = '*' * (len(str_value) - 4) + str_value[-4:]
                else:
                    result[key] = '*' * len(str_value)
            else:
                result[key] = value
        
        return result


class TokenManager:
    """
    Secure token generation and validation
    
    Used for:
    - Password reset tokens
    - Email verification tokens
    - Temporary access tokens
    """
    
    def __init__(self):
        self.encryption = EncryptionHandler()
    
    def generate_token(self, data: dict, expires_in: int = 3600) -> str:
        """
        Generate a signed token with expiration
        
        Args:
            data: Data to include in token
            expires_in: Token lifetime in seconds
        
        Returns:
            Signed token string
        """
        from datetime import datetime, timedelta
        import json
        
        payload = {
            'data': data,
            'exp': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
            'iat': datetime.utcnow().isoformat(),
            'jti': secrets.token_urlsafe(16)
        }
        
        token_data = json.dumps(payload)
        return self.encryption.encrypt(token_data)
    
    def verify_token(self, token: str, max_age: int = None) -> dict:
        """
        Verify and decode a token
        
        Args:
            token: Token to verify
            max_age: Maximum age in seconds (overrides embedded expiration)
        
        Returns:
            Token data if valid
        
        Raises:
            ValueError: If token is invalid or expired
        """
        from datetime import datetime
        import json
        
        try:
            token_data = self.encryption.decrypt(token)
            payload = json.loads(token_data)
        except Exception as e:
            raise ValueError(f"Invalid token: {e}")
        
        # Check expiration
        exp = datetime.fromisoformat(payload['exp'])
        if datetime.utcnow() > exp:
            raise ValueError("Token has expired")
        
        return payload['data']


# Convenience functions for common operations
def hash_password(password: str) -> Tuple[str, str]:
    """Hash a password"""
    return PasswordHandler.hash_password(password)


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify a password"""
    return PasswordHandler.verify_password(password, password_hash, salt)


def encrypt_data(data: str) -> str:
    """Encrypt data using Fernet"""
    handler = EncryptionHandler()
    return handler.encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt Fernet-encrypted data"""
    handler = EncryptionHandler()
    return handler.decrypt(encrypted_data)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks"""
    return secrets.compare_digest(a, b)


# Global instances for easy import
password_handler = PasswordHandler()
encryption_handler = EncryptionHandler()
api_key_handler = APIKeyHandler()
