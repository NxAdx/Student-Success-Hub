import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings


def _get_fernet_key():
    """Derive a Fernet-compatible key from Django's SECRET_KEY."""
    secret = settings.SECRET_KEY.encode('utf-8')
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_api_key(plain_key: str) -> str:
    """Encrypt an API key for database storage."""
    f = Fernet(_get_fernet_key())
    return f.encrypt(plain_key.encode('utf-8')).decode('utf-8')


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from database storage."""
    f = Fernet(_get_fernet_key())
    return f.decrypt(encrypted_key.encode('utf-8')).decode('utf-8')
