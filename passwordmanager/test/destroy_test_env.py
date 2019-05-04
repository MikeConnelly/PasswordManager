import shutil
import os


def destroy_env():
    if os.path.exists('./passwordmanager/tests/data/'):
        shutil.rmtree('./passwordmanager/tests/data/')
