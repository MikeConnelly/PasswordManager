import sys
import os
import shutil
import json
from passwordmanager.src import password_manager
from passwordmanager.interface import interface, gui


def get_paths(path_file):
    """Returns contents of the ./docs/paths.txt file as a dictionary"""
    with open(path_file, 'r') as j:
        paths = json.load(j)
        if not 'key_path' in paths:
            print('---key path not found in paths.json, creating default key path---')
            paths['key_path'] = './passwordmanager/data/key.bin'
        if not 'database_path' in paths:
            print('---database path not found in paths.json, creating default database path---')
            paths['database_path'] = './passwordmanager/data/pmdb.sqlite'

    return paths


def change_key_dir(path_file, path_dict, new_dir):
    """
    Change the directory where the key is stored.\n
    If a key already exists move it to the new directory.
    """
    new_path = new_dir + 'key.bin'
    key_path = path_dict['key_path']

    if os.path.isfile(key_path):
        shutil.move(key_path, new_path)
        print('---key file moved---')

    with open(path_file, 'r') as j:
        filedata = json.load(j)

    filedata['key_path'] = new_path
    with open(path_file, 'w') as j:
        json.dump(filedata, path_file)


def change_database_dir(path_file, path_dict, new_dir):
    """
    Change the directory where the database is stored.\n
    If a database already exists move it to the new directory.
    """
    new_path = new_dir + 'pmdb.sqlite'
    database_path = path_dict['database_path']

    if os.path.isfile(database_path):
        shutil.move(database_path, new_path)
        print('---database file moved---')

    with open(path_file, 'r') as j:
        filedata = json.load(j)

    filedata['database_path'] = new_path
    with open(path_file, 'w') as j:
        json.dump(filedata, path_file)


def main(args):
    """main docstirng"""
    if not os.path.exists('./passwordmanager/data/'):
        os.makedirs('./passwordmanager/data/')

    path_file = './passwordmanager/data/paths.json'
    if not os.path.isfile(path_file):
        path_data = {
            'database_path': '/passwordmanager/data/pmdb.sqlite',
            'key_path': './passwordmanager/data/key.bin'
        }
        with open(path_file, 'w') as j:
            json.dump(path_data, j)

    paths = get_paths(path_file)

    if len(args) > 1:
        arg = args[1]
    else:
        arg = 'cli'

    if arg == 'cli':
        pm = password_manager.PasswordManager(paths)
        interface.run(pm)

    elif arg == 'gui':
        pm = password_manager.PasswordManager(paths)
        gui.run(args, pm)

    elif arg == 'key_dir':
        print('Enter new key directory')
        new_key_dir = input()

        if os.path.exists(new_key_dir):
            change_key_dir(path_file, paths, new_key_dir)
            paths = get_paths(path_file)
            print('---key path updated---')
        else:
            print('---specified path does not exist---')
            exit()

    elif arg == 'database_dir':
        print('Enter new database directory')
        new_database_dir = input()

        if os.path.exists(new_database_dir):
            change_database_dir(path_file, paths, new_database_dir)
            paths = get_paths(path_file)
            print('---database path updated---')
        else:
            print('---specified path does not exist---')
            exit()
