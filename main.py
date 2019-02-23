import sys
import os
import shutil
from passwordmanager import password_manager


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
        key_path = paths['key_path']
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
        database_path = paths['database_path']
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


if __name__ == '__main__':

    path_file = './docs/paths.txt'

    if os.path.isfile(path_file):
        paths = get_paths(path_file)
    else:
        raise(EnvironmentError)

    for arg in sys.argv:

        if arg == '--key_dir':
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
    
    if not os.path.exists('./data/'):
        os.makedirs('./data/')

    pm = password_manager.PasswordManager(paths)

    while pm.user == None:

        print('enter login or newuser')
        command = input()

        if command == 'newuser':
            pm.create_user_cmd()
        elif command == 'login':
            pm.login_cmd()
        else:
            print('invalid command')

    pm.get_user_command()
