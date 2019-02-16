import sys
import os
from passwordmanager import password_manager
from passwordmanager import crypto


def get_paths(path_file):
    """
    Returns contents of the ./docs/paths.txt file as a dictionary
    """

    paths = []
    with open(path_file, 'r') as f:
        paths=f.read().split('\n')

    path_dict = {}
    for line in paths:
        if line:
            path = line.split('=')
            path_dict[path[0]] = path[1]

    return path_dict


if __name__ == '__main__':

    print(sys.argv)

    path_file = './docs/paths.txt'
    if os.path.isfile(path_file):
        paths = get_paths(path_file)
    else:
        raise(EnvironmentError)

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
