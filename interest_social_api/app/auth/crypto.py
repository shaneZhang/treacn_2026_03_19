import os
import hashlib
import secrets
import base64
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PasswordHandler:
    ITERATIONS = 260000
    HASH_ALGORITHM = 'sha256'
    SALT_LENGTH = 16
    HASH_LENGTH = 32

    @staticmethod
    def generate_salt() -> str:
        return secrets.token_hex(PasswordHandler.SALT_LENGTH)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if salt is None:
            salt = PasswordHandler.generate_salt()

        if len(salt) != PasswordHandler.SALT_LENGTH * 2:
            raise ValueError(f"Salt must be {PasswordHandler.SALT_LENGTH * 2} characters long")

        hash_value = hashlib.pbkdf2_hmac(
            PasswordHandler.HASH_ALGORITHM,
            password.encode('utf-8'),
            salt.encode('utf-8'),
            PasswordHandler.ITERATIONS,
            dklen=PasswordHandler.HASH_LENGTH
        )

        password_hash = base64.b64encode(hash_value).decode('utf-8')
        return password_hash, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        try:
            computed_hash, _ = PasswordHandler.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, password_hash)
        except Exception:
            return False

    @staticmethod
    def generate_password(length: int = 16) -> str:
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

class EncryptionHandler:
    def __init__(self):
        self.key = self._get_or_generate_key()
        self.fernet = Fernet(self.key)

    def _get_or_generate_key(self) -> bytes:
        key = os.environ.get('ENCRYPTION_KEY')
        if key:
            try:
                return base64.urlsafe_b64decode(key.encode())
            except Exception:
                pass

        master_key = os.environ.get('APP_SECRET_KEY', secrets.token_hex(32))
        salt = os.environ.get('SECURITY_PASSWORD_SALT', secrets.token_hex(16))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return key

    def encrypt(self, data: str) -> str:
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()

class APIKeyHandler:
    KEY_PREFIX = 'isk_'
    KEY_LENGTH = 32

    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        random_bytes = secrets.token_bytes(APIKeyHandler.KEY_LENGTH)
        key = APIKeyHandler.KEY_PREFIX + secrets.token_urlsafe(APIKeyHandler.KEY_LENGTH)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash

    @staticmethod
    def verify_api_key(api_key: str, key_hash: str) -> bool:
        if not api_key.startswith(APIKeyHandler.KEY_PREFIX):
            return False
        computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, key_hash)

    @staticmethod
    def generate_api_key_id() -> str:
        return f"key_{secrets.token_urlsafe(8)}"

password_handler = PasswordHandler()
encryption_handler = EncryptionHandler()
api_key_handler = APIKeyHandler()
