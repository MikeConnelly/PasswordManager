import shutil
import os


def destroy_env():
    destroy_docs()
    destroy_data()

def destroy_docs():
    if os.path.exists('./tests/docs/'):
        shutil.rmtree('./tests/docs/')

def destroy_data():
    if os.path.exists('./tests/data/'):
        shutil.rmtree('./tests/data/')
