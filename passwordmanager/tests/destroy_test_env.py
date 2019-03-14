import shutil
import os


def destroy_env():
    destroy_docs()
    destroy_data()

def destroy_docs():
    if os.path.exists('./passwordmanager/tests/docs/'):
        shutil.rmtree('./passwordmanager/tests/docs/')

def destroy_data():
    if os.path.exists('./passwordmanager/tests/data/'):
        shutil.rmtree('./passwordmanager/tests/data/')
