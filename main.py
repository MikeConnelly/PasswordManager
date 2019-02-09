import sys
from passwordmanager import password_manager


if __name__ == '__main__':

    pm = password_manager.PasswordManager()

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
