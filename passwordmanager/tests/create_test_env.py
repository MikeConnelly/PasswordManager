import os
import json


def init_env():

    try:
        os.makedirs('./passwordmanager/tests/data/')
    except OSError:
        return False

    with open('./passwordmanager/tests/data/paths.json', 'w') as j:
        path_data = {
            'database_path': '/passwordmanager/tests/data/pmdb.sqlite',
            'key_path': './passwordmanager/tests/data/key.bin'
        }
        json.dump(path_data, j)

    return True
