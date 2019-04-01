import os
from cryptography.fernet import Fernet


class Crypto:

    def __init__(self, key_path):
        self.key_file = key_path
        if not os.path.isfile(self.key_file):
            self.init_key()

    def init_key(self):
        """create new encryption key"""
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)

    def encrypt(self, field):
        """encrypt account field"""
        key = None
        with open(self.key_file, 'rb') as f:
            key = f.read()

        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(bytes(field.encode()))

        return ciphered_text

    def decrypt(self, hashed_field):
        """decrypt account field"""
        key = None
        with open(self.key_file, 'rb') as f:
            key = f.read()

        cipher_suite = Fernet(key)
        uncipher_text = (cipher_suite.decrypt(hashed_field))
        password = bytes(uncipher_text).decode('utf-8')

        return password
