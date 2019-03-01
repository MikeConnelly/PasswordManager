

class Interface:

    def __init__(self, pm):
        self.pm = pm
    
    def get_user(self):
        
        while self.pm.user == None:

            print('enter login or newuser')
            command = input()

            if command == 'newuser':
                self.create_user_cmd()
            elif command == 'login':
                self.login_cmd()
            else:
                print('invalid command')
            
        self.get_cmd()
    
    def get_cmd(self):
    
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
                '5': self.pm.logout
            }

            try:
                commands[input()]()
            except KeyError:
                print('---invalid input---')
    
    def create_user_cmd(self):

        print('Enter username: ')
        username = input()
        masterpass = ''

        while not masterpass:

            print('Create password: ')
            masterpass = input()

            print('Confirm password: ')
            if input() != masterpass:
                masterpass = ''

        self.pm.create_user(username, masterpass)

    def login_cmd(self):

        print('Enter username: ')
        username = input()
        print('Enter password: ')
        password = input()

        self.pm.login(username, password)
    
    def retrieve_table_cmd(self):

        table = self.pm.retrieve_table()

        for account in table:
            print('Service: ' + account['name'] + ', Email ' + account['email'] + ', Password: ' + account['password'])

    def add_user_entry_cmd(self):

        print('Account: ')
        account = input()

        print('Username: ')
        username = input()

        print('Password: ')
        password = input()

        self.pm.add_user_entry(account, username, password)
        print('---account added---')

    def select_user_account_cmd(self, mode):
        
        table = self.pm.user.accounts

        selection = None
        index = 1
        map = {}
        for account in table:
            map[index] = account
            print('Index: ' + str(index) + ', Service: ' + account.name)
            index += 1

        while not selection:
            print('Enter the index of the service you want to ' + mode)
            try:
                selection = map[int(input())]
            except (KeyError, ValueError):
                print('---invalid input---')
        
        return selection
    
    def remove_entry_cmd(self):
        
        selection = self.select_user_account_cmd('remove')
        self.pm.remove_entry(selection)
        print(selection.name + ' successfully removed')
    
    def change_entry_cmd(self):
        
        selection = self.select_user_account_cmd('change')

        field_selection = None
        fields = {
            1: selection.name,
            2: selection.email,
            3: selection.url,
            4: selection.password
        }

        for field in fields:
            print('1: name ' + field)
        
        while not field_selection:
            print('Enter the index of the field you want to change')
            try:
                i = input()
                field = fields[i]
            except KeyError:
                print('---invalid input---')

        print('enter new field')
        new_field = input()

        self.pm.change_entry(selection, field_selection, new_field)
