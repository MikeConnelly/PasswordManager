import os
import sys


def init_env():

    try:
        os.makedirs('./passwordmanager/tests/docs/')
    except OSError:
        return False

    with open('./passwordmanager/tests/docs/paths.txt', 'w') as f:
        f.write('database_path=/passwordmanager/tests/data/pmdb.sqlite\n')
        f.write('key_path=./passwordmanager/tests/data/key.bin\n')
    
    try:
        os.makedirs('./passwordmanager/tests/data/')
    except OSError:
        return False
    
    return True
