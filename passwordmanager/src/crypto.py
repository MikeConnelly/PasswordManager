from cryptography.fernet import Fernet
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Cipher:
    """
    Used to encrypt and decrypt account fields in the database
    """

    def __init__(self, key):
        self.cipher_suite = Fernet(key)

    def encrypt(self, field):
        """encrypt account field"""
        ciphered_text = self.cipher_suite.encrypt(str.encode(field))
        return ciphered_text

    def decrypt(self, hashed_field):
        """decrypt account field"""
        plaintext = bytes(self.cipher_suite.decrypt(hashed_field)).decode('utf-8')
        return plaintext


def get_hashed_password(password):
    """create a password suitable to store"""
    ph = PasswordHasher()
    hashed = ph.hash(password)
    return hashed


def compare_passwords(password, stored_password):
    """compares a plaintext password with the stored, encrypted password"""
    ph = PasswordHasher()
    try:
        ph.verify(stored_password, password)
        if ph.check_needs_rehash(stored_password):
            return (True, True)
        return (True, False)
    except VerifyMismatchError:
        return (False, False)


def generate_key():
    """generate new key"""
    return Fernet.generate_key()
