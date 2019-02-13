import os.path
from cryptography.fernet import Fernet


class Crypto:

    def __init__(self):

        self.key_file = '/data/key.txt'

        if not os.path.isfile(self.key_file):
            self.init_key()
        else:
            print('stored!')

    def init_key(self):

        key = Fernet.generate_key()
        key_string = key.decode()

        f = open('/data/key.txt','a+')
        f.write(key_string)
        f.close()

    def encrypt(password):
        pass

    def decrypt(password):
        pass
