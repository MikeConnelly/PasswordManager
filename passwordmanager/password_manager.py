'''
to-do:
 - create a file that holds the directories of key and db for different users
 - use absolute file paths for simplicity
'''
from .crypto import Crypto
from .models import Base, Service, User
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class PasswordManager:

    def __init__(self, paths):

        self.user = None
        self.sqlite_file = paths['database_path']
        self.crypto = Crypto(paths['key_path'])

        if not os.path.isfile(self.sqlite_file):
            engine = create_engine('sqlite://' + self.sqlite_file)
            Base.metadata.create_all(bind=engine)
        else:
            engine = create_engine('sqlite://' + self.sqlite_file)
            Base.metadata.bind = engine

        Session = sessionmaker(bind=engine)
        self.session = Session()


    def add_user_to_master(self, username, masterpass):

        # check if user already exists
        list = self.session.query(User).filter(User.username == username).all()

        if list != []:
            raise UserError
        else:
            hashed_masterpass = self.crypto.encrypt(masterpass)

            user = User()
            user.username = username
            user.master_password = hashed_masterpass

            self.session.add(user)
            self.session.commit()

    def login(self, username, password):

        user = self.session.query(User).filter(User.username == username).one()

        try:
            hashed_pass = user.master_password
            masterpass = self.crypto.decrypt(hashed_pass)

            if masterpass == password:
                print('---login successful---')
                self.user = user
            else:
                print('---invalid password---')
        except IndexError:
            print('---user does not exist---')

    def create_user(self, username, masterpass):

        try:
            self.add_user_to_master(username, masterpass)
            self.login(username, masterpass)
        except UserError:
            print('---user already exists---')

    def retrieve_table(self):

        table = self.user.services

        for service in table:
            password = self.crypto.decrypt(service.password)
            print('Service: ' + service.name + ', Email ' + service.email + ', Password: ' + password)

    def add_user_entry(self, service_name, service_email, service_password):

        hashed_pass = self.crypto.encrypt(service_password)

        service = Service()
        service.name = service_name
        service.email = service_email
        service.password = hashed_pass
        service.user_id = self.user.id

        self.session.add(service)
        self.session.commit()

    def remove_entry(self):

        table = self.user.services

        selection = None
        index = 1
        map = {}
        for service in table:
            map[index] = service
            print('Index: ' + str(index) + ', Service: ' + service.name)
            index += 1

        while not selection:
            print('Enter the index of the service you want to remove')
            try:
                selection = map[int(input())]
            except (KeyError, ValueError):
                print('---invalid input---')

        print(selection.name + ' successfully removed')
        self.session.delete(selection)
        self.session.commit()

    def change_entry(self):
        '''
        CURRENTLY NOT WORKING
        '''

        table = self.user.services

        selection = None
        index = 1
        map = {}
        for service in table:
            map[index] = service
            print('Index: ' + str(index) + ', Service: ' + service.name)
            index += 1

        while not selection:
            print('Enter the index of the service you want to change')
            try:
                selection = map[int(input())]
            except (KeyError, ValueError):
                print('---invalid input---')

        field = None
        fields = {
            'name': selection.name,
            'email': selection.email,
            'url': selection.url,
            'password': selection.password
        }
        print('which field would you like to edit: name, email, url, or password?')
        while not field:
            try:
                i = input()
                field = fields[i]
            except KeyError:
                print('---invalid input---')

        print('enter new ' + i)
        print(fields[i])
        fields[i] = input()
        self.session.commit()

    def logout(self):

        self.session.close()
        exit(0)

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

        self.create_user(username, masterpass)

    def login_cmd(self):

        print('Enter username: ')
        username = input()
        print('Enter password: ')
        password = input()

        self.login(username, password)

    def add_user_entry_cmd(self):

        print('Service: ')
        service = input()

        print('Username: ')
        username = input()

        print('Password: ')
        password = input()

        self.add_user_entry(service, username, password)

    def get_user_command(self):

        while True:
            print('1: retrieve table')
            print('2: add an entry')
            print('3: remove an entry')
            print('4: change an entry')
            print('5: logout')

            commands = {
                '1': self.retrieve_table,
                '2': self.add_user_entry_cmd,
                '3': self.remove_entry,
                '4': self.change_entry,
                '5': self.logout
            }

            try:
                commands[input()]()
            except KeyError:
                print('---invalid input---')


class UserError(Exception):
    pass
