from passwordmanager.src.password_manager import UserError, AccountError


class Interface:
    '''
    command line interface for password manager
    '''
    def __init__(self, pm):
        self.pm = pm

    def get_user(self):
        '''create new user or continue to login'''
        while self.pm.user is None:
            print('enter login or newuser')
            command = input()

            if command == 'newuser':
                self.create_user_cmd()
            elif command == 'login':
                self.login_cmd()
            else:
                print('---invalid command---')

        self.get_cmd()

    def get_cmd(self):
        '''main application loop to execute user commands'''
        while True:
            print('1: retrieve table')
            print('2: add an entry')
            print('3: remove an entry')
            print('4: change an entry')
            print('5: logout')

            commands = {
                '1': self.retrieve_table_cmd,
                '2': self.add_user_entry_cmd,
                '3': self.remove_entry_cmd,
                '4': self.change_entry_cmd,
                '5': self.logout_cmd
            }

            try:
                commands[input()]()
            except KeyError:
                print('---invalid input---')

    def create_user_cmd(self):
        '''CLI to create new user'''
        while self.pm.user is None:
            print('Enter username: ')
            username = input()
            masterpass = ''

            while not masterpass:
                print('Create password: ')
                masterpass = input()

                print('Confirm password: ')
                if input() != masterpass:
                    print('---Password do not match---')
                    masterpass = ''

            try:
                self.pm.create_user_and_login(username, masterpass)
            except UserError as err:
                print(str(err))

    def login_cmd(self):
        '''CLI to login'''
        while not self.pm.user:
            print('Enter username: ')
            username = input()
            print('Enter password: ')
            password = input()

            try:
                self.pm.login(username, password)
            except UserError as err:
                print(str(err))

    def retrieve_table_cmd(self):
        '''prints the current user's table of accounts'''
        table = self.pm.retrieve_table()

        print('---table---')
        for account in table:
            print(f"Account: {account['name']}, Email: {account['email']}, Password: {account['password']}, URL: {account['url']}")
        print('-----------')

    def add_user_entry_cmd(self):
        '''CLI to add an account for the current user'''
        print('---add an entry or type "exit"---')

        try:
            print('Account: ')
            account = get_input_or_exit()

            print('Email: ')
            username = get_input_or_exit()

            print('Password: ')
            password = get_input_or_exit()

            print('URL (optional): ')
            url = get_input_or_exit()
        except ExitError:
            return

        try:
            self.pm.add_user_entry(account, username, password, url)
            print('---account added---')
        except AccountError as err:
            print(str(err))

    def select_user_account_cmd(self, mode):
        '''
        print user accounts and return the one selected\n
        raises ExitError
        '''
        table = self.pm.retrieve_table()

        selection = None
        index = 1
        account_map = {}
        for account in table:
            account_map[index] = account
            print(str(index) + ': ' + account['name'])
            index += 1

        while not selection:
            print(f"Enter the index of the account you want to {mode} or \"exit\"")
            try:
                selection = account_map[int(get_input_or_exit())]
            except (KeyError, ValueError):
                print('---invalid input---')

        return selection

    def remove_entry_cmd(self):
        '''user selects an account to remove'''
        print('---remove an entry---')

        try:
            selection = self.select_user_account_cmd('remove')
            self.pm.remove_entry(selection)
        except ExitError:
            return

        print(selection['name'] + ' successfully removed')

    def change_entry_cmd(self):
        '''user selects and account and field to update'''
        print('---change an entry---')
        try:
            selection = self.select_user_account_cmd('change')
        except ExitError:
            return

        fields = {
            1: selection['name'],
            2: selection['email'],
            3: selection['password'],
            4: selection['url']
        }
        cols = {
            1: 'name',
            2: 'email',
            3: 'password',
            4: 'url'
        }

        for key, value in fields.items():
            print(str(key) + '. ' + cols[key] + ': ' + str(value))

        col_selection = None
        while not col_selection:
            print("Enter the index of the field you want to change or \"exit\"")
            try:
                i = int(get_input_or_exit())
                col_selection = cols[i]
            except (KeyError, ValueError):
                print('---invalid input---')
            except ExitError:
                return

        print('enter new field')
        new_field = input()

        self.pm.change_entry(selection, col_selection, new_field)
        print('---account successfully updated---')

    def logout_cmd(self):
        '''logout and exit'''
        self.pm.logout()
        exit(0)


def run(pm):
    '''starts command line interface'''
    cli = Interface(pm)
    cli.get_user()


def get_input_or_exit():
    '''get user input or raise ExitError'''
    value = input()
    if value == 'exit':
        raise ExitError
    return value


class ExitError(Exception):
    '''exception raised when exiting a function through get_input_or_exit'''
