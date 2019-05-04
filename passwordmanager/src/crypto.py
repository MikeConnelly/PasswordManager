import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Cipher:

    def __init__(self, key):
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, field):
        """encrypt account field"""
        ciphered_text = self.cipher_suite.encrypt(str.encode(field))
        return ciphered_text

    def decrypt(self, hashed_field):
        """decrypt account field"""
        plaintext = bytes(self.cipher_suite.decrypt(hashed_field)).decode('utf-8')
        return plaintext


def create_new_key(password, salt=None):
    """create a new encryption key and it's salt from a given password"""
    salt = salt if salt is not None else os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(str.encode(password))
    return (key, salt)

def get_encrypted_password(password):
    """create a password suitable to store"""
    key, salt = create_new_key(password)
    fernet = Fernet(base64.urlsafe_b64encode(key))
    ciphertext = fernet.encrypt(str.encode(password))
    ciphertext_with_salt = ciphertext + base64.urlsafe_b64encode(salt)
    return ciphertext_with_salt

def compare_passwords(password, stored_password):
    """compares a plaintext password with the stored, encrypted password"""
    ciphertext = stored_password[:-16]
    salt = stored_password[-24:]
    key, _ = create_new_key(password, base64.urlsafe_b64decode(salt))
    fernet = Fernet(base64.urlsafe_b64encode(key))
    try:
        plaintext = fernet.decrypt(ciphertext).decode('utf-8')
        if plaintext == password:
            return (True, Cipher(key))
    except InvalidToken:
        pass
    return (False, None)
