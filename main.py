import sys
import os
import shutil
from src import password_manager, interface


def get_paths(path_file):
    """
    Returns contents of the ./docs/paths.txt file as a dictionary
    """

    with open(path_file, 'r') as f:
        paths=f.read().split('\n')

    path_dict = {}
    for line in paths:
        if line:
            path = line.split('=')
            path_dict[path[0]] = path[1]

    return path_dict


def change_key_dir(path_file, path_dict, new_dir):
    """
    Change the directory where the key is stored.
    If a key already exists move it to the new directory.
    """

    new_path = new_dir + 'key.bin'

    try:
        key_path = path_dict['key_path']
    except KeyError:
        print('---key_path does not exist in ./docs/paths.txt---')
        exit()

    if os.path.isfile(key_path):
        shutil.move(key_path, new_path)
        print('---key file moved---')

    with open(path_file, 'r') as f:
        filedata = f.read()

    filedata = filedata.replace(key_path, new_path)

    with open(path_file, 'w') as f:
        f.write(filedata)


def change_database_dir(path_file, path_dict, new_dir):
    """
    Change the directory where the database is stored.
    If a database already exists move it to the new directory.
    """

    new_path = new_dir + 'pmdb.sqlite'

    try:
        database_path = path_dict['database_path']
    except KeyError:
        print('---database_path does not exist in ./docs/paths.txt---')
        exit()

    if os.path.isfile(database_path):
        shutil.move(database_path, new_path)
        print('---database file moved---')

    with open(path_file, 'r') as f:
        filedata = f.read()

    filedata = filedata.replace(database_path, new_path)

    with open(path_file, 'w') as f:
        f.write(filedata)


def main():

    path_file = './docs/paths.txt'

    if os.path.isfile(path_file):
        paths = get_paths(path_file)
    else:
        raise(EnvironmentError)
    
    if not os.path.exists('./data/'):
        os.makedirs('./data/')

    for arg in sys.argv:

        if arg == 'cli':
            pm = password_manager.PasswordManager(paths)
            cli = interface.Interface(pm)

            cli.get_user()

        elif arg == '--key_dir':
            print('Enter new key directory')
            new_key_dir = input()

            if os.path.exists(new_key_dir):
                change_key_dir(path_file, paths, new_key_dir)
                paths = get_paths(path_file)
                print('---key path updated---')
            else:
                print('---specified path does not exist---')
                exit()

        elif arg == '--database_dir':
            print('Enter new database directory')
            new_database_dir = input()

            if os.path.exists(new_database_dir):
                change_database_dir(path_file, paths, new_database_dir)
                paths = get_paths(path_file)
                print('---database path updated---')
            else:
                print('---specified path does not exist---')
                exit()


if __name__ == '__main__':
    
    main()
