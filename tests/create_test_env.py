import os
import sys
import main
from main import main
# sys.path.append(sys.path[0][:-5])


def init_env():

    try:
        os.makedirs('./tests/docs/')
    except OSError:
        return False

    with open('./tests/docs/paths.txt', 'w') as f:
        f.write('database_path=/tests/data/pmdb.sqlite\n')
        f.write('key_path=./tests/data/key.bin\n')
    
    try:
        os.makedirs('./tests/data/')
    except OSError:
        return False
    
    return True
