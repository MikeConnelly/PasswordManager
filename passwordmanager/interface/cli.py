from getpass import getpass
from passwordmanager.src.password_manager import UserError, AccountError


class Interface:
    """
    command line interface for password manager
    """

    def __init__(self, pm):
        self.pm = pm

    def get_user(self):
        """create new user or continue to login"""
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
        """main application loop to execute user commands"""
        while True:
            print('1: retrieve table')
            print('2: add an account')
            print('3: change an account')
            print('4: remove an account')
            print('5: add a field')
            print('6: rename a field')
            print('7: remove a field')
            print('8: logout')
            print('9: reset')
            commands = {
                '1': self.retrieve_table_cmd,
                '2': self.add_account_cmd,
                '3': self.change_account_cmd,
                '4': self.remove_account_cmd,
                '5': self.add_column_cmd,
                '6': self.rename_column_cmd,
                '7': self.remove_column_cmd,
                '8': self.logout_cmd,
                '9': self.reset_cmd
            }
            try:
                commands[input()]()
            except KeyError:
                print('---invalid input---')

    def create_user_cmd(self):
        """CLI to create new user"""
        while self.pm.user is None:
            print('Enter username: ')
            username = input()
            masterpass = ''

            while not masterpass:
                print('Create password: ')
                masterpass = getpass(prompt='')
                print('Confirm password: ')
                if getpass(prompt='') != masterpass:
                    print('---Password do not match---')
                    masterpass = ''

            try:
                self.pm.create_user_and_login(username, masterpass)
            except UserError as err:
                print(str(err))

    def login_cmd(self):
        """CLI to login"""
        while not self.pm.user:
            print('Enter username: ')
            username = input()
            print('Enter password: ')
            password = getpass(prompt='')

            try:
                self.pm.login(username, password)
            except UserError as err:
                print(str(err))

    def retrieve_table_cmd(self):
        """prints the current user's table of accounts"""
        table = self.pm.retrieve_table()

        print('---table---')
        for account in table:
            index = 1
            length = len(account)
            for field, value in account.items():
                end = '\n' if index == length else ', '
                print(f"{field}: {value}", end=end)
                index += 1
        print('-----------')

    def add_account_cmd(self):
        """CLI to add an account for the current user"""
        print('---add an account or type "exit"---')
        custom_cols = self.pm.get_custom_columns()
        expansion = {}

        try:
            print('Account: ')
            account = get_input_or_exit()
            print('Email: ')
            username = get_input_or_exit()
            print('Password: ')
            password = get_input_or_exit(password=True)
            print('URL (optional): ')
            url = get_input_or_exit()
            for col in custom_cols:
                print(f"{col} (optional): ")
                value = get_input_or_exit()
                if value:
                    expansion[col] = value
        except ExitError:
            return

        try:
            self.pm.add_account(account, username, password, url, expansion)
            print('---account added---')
        except AccountError as err:
            print(str(err))

    def select_account_cmd(self, mode='remove or change'):
        """
        print user accounts and return the one selected\n
        raises ExitError
        """
        table = self.pm.retrieve_table()
        selection = None
        account_map = {}
        for index, account in enumerate(table, start=1):
            account_map[index] = account
            print(str(index) + ': ' + account['name'])

        while not selection:
            print(f"Enter the index of the account you want to {mode} or \"exit\"")
            try:
                selection = account_map[int(get_input_or_exit())]
            except (KeyError, ValueError):
                print('---invalid input---')

        return selection

    def remove_account_cmd(self):
        """user selects an account to remove"""
        print('---remove an account---')
        try:
            selection = self.select_account_cmd('remove')
            confirmation = ''
            while confirmation not in ('y', 'Y'):
                print(f"are you sure you want to remove {selection['name']}? (y/n):")
                confirmation = input()
                if confirmation in ('n', 'N'):
                    return
            self.pm.remove_account(selection)
        except ExitError:
            return

        print(selection['name'] + ' successfully removed')

    def change_account_cmd(self):
        """user selects an account and field to update"""
        print('---change an account---')
        try:
            selection = self.select_account_cmd('change')
        except ExitError:
            return

        all_fields = self.pm.get_all_columns()
        cols = {}
        for index, field in enumerate(all_fields, start=1):
            value = selection[field] if field in selection else ''
            print(f"{index}. {field}: {value}")
            cols[str(index)] = field

        col_selection = None
        while not col_selection:
            print("Enter the index of the field you want to change or \"exit\"")
            is_password = col_selection == 'password'
            try:
                col_selection = cols[get_input_or_exit(password=is_password)]
            except (KeyError, ValueError):
                print('---invalid input---')
            except ExitError:
                return
        print('enter new field')
        new_field = input()
        self.pm.change_account(selection, col_selection, new_field)
        print('---account successfully updated---')

    def add_column_cmd(self):
        """CLI to add a column to the user's table of accounts"""
        print('---enter new column name or "exit"---')
        try:
            name = get_input_or_exit()
            self.pm.add_column(name)
        except UserError as err:
            print(str(err))
        except ExitError:
            return

    def select_custom_column_cmd(self, mode='rename or remove'):
        """select column from custom columns"""
        print('---enter the index of the column you wish to rename---')
        custom_columns = self.pm.get_custom_columns()
        selection = None
        column_map = {}
        for index, col in enumerate(custom_columns, start=1):
            column_map[index] = col
            print(str(index) + ': ' + col)
        while not selection:
            print(f"Enter the index of the column you want to {mode} or \"exit\"")
            try:
                selection = column_map[int(get_input_or_exit())]
            except (KeyError, ValueError):
                print('---invalid input---')
        return selection

    def rename_column_cmd(self):
        """CLI to rename a custom column in the user's account table"""
        try:
            name = self.select_custom_column_cmd(mode='rename')
        except ExitError:
            return
        print('Enter new column name:')
        new_name = input()
        self.pm.rename_column(name, new_name)

    def remove_column_cmd(self):
        """CLI to remove a custom column from the user's account table"""
        try:
            name = self.select_custom_column_cmd(mode='remove')
            confirmation = ''
            while confirmation not in ('y', 'Y'):
                print(f"are you sure you want to remove column {name}? (y/n):")
                confirmation = input()
                if confirmation in ('n', 'N'):
                    return
            self.pm.remove_column(name)
        except ExitError:
            return
        print(f"{name} successfully removed")

    def logout_cmd(self):
        """logout and exit"""
        self.pm.logout()
        exit(0)

    def reset_cmd(self):
        pass


def run(pm):
    """starts command line interface"""
    cli = Interface(pm)
    cli.get_user()


def get_input_or_exit(password=False):
    """get user input or raise ExitError"""
    value = getpass(prompt='') if password else input()
    if value == 'exit':
        raise ExitError
    return value


class ExitError(Exception):
    """exception raised when exiting a function through get_input_or_exit"""
