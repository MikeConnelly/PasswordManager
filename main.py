import sys
import os
from passwordmanager import password_manager
from passwordmanager import crypto


if __name__ == '__main__':

    path_file = 'paths.txt'
    if os.path.isfile(path_file):
        paths = get_paths(path_file)

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


'''
return paths file as a dictionary
'''
def get_paths():

    paths = []
    with open(path_file, 'r') as f:
        paths=f.read().split(',')

    path_dict = {}
    for line in paths:
        path = line.split('=')
        path_dict[path[0]) = path[1]

    return path_dict
