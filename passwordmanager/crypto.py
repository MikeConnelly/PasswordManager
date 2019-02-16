import os
from cryptography.fernet import Fernet


class Crypto:

    def __init__(self, key_path):

        self.key_file = key_path

        if not os.path.isfile(self.key_file):
            self.init_key()

    def init_key(self):

        key = Fernet.generate_key()

        with open(self.key_file, 'wb') as f:

            f.write(key)

    def encrypt(self, password):

        key = None

        with open(self.key_file, 'rb') as f:

            key = f.read()

        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(bytes(password.encode()))

        return ciphered_text

    def decrypt(self, cipher_text):

        key = None

        with open(self.key_file, 'rb') as f:

            key = f.read()

        cipher_suite = Fernet(key)
        uncipher_text = (cipher_suite.decrypt(cipher_text))
        password = bytes(uncipher_text).decode('utf-8')

        return password
