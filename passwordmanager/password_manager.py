'''
to-do:
 - look into / change database library to sqalchemy
'''
import os
import sqlite3
from .user import User
from .crypto import Crypto


class PasswordManager:

    def __init__(self):

        if not os.path.exists('./data/'):
            os.makedirs('./data/')

        self.user = None
        self.sqlite_file = './data/pmdb.sqlite'
        self.crypto = Crypto()

        if not os.path.isfile(self.sqlite_file):
            self.create_db()
        else:
            self.conn = sqlite3.connect(self.sqlite_file)
            self.cursor = self.conn.cursor()

    def create_db(self):

        table_name = 'USER_DATABASE'
        field_1 = 'USER'
        field_2 = 'MASTER_PASSWORD'
        field_type = 'TEXT'

        self.conn = sqlite3.connect(self.sqlite_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE {tn} ({f1} {ft}, {f2} {ft})"
                  .format(tn=table_name, f1=field_1, f2=field_2, ft=field_type))

        self.conn.commit()

    def add_user_to_master(self, username, masterpass):

        # check if user already exists
        self.cursor.execute("SELECT * FROM USER_DATABASE WHERE USER = ?", (username,))
        row = self.cursor.fetchall()

        if row != []:
            raise UserError
        else:
            hashed_masterpass = self.crypto.encrypt(masterpass)
            params = (username, hashed_masterpass)
            self.cursor.execute("INSERT INTO USER_DATABASE (USER, MASTER_PASSWORD) VALUES (?, ?)", params)

            self.conn.commit()

    def create_user_table(self, username):

        table_name = username + '_PASSWORD_DATABASE'
        field_1 = 'SERVICE'
        field_2 = 'USERNAME'
        field_3 = 'PASSWORD'
        field_type = 'TEXT'

        try:
            self.cursor.execute("CREATE TABLE {tn} ({f1} {ft}, {f2} {ft}, {f3} {ft})"
                      .format(tn=table_name, f1=field_1, f2=field_2, f3=field_3, ft=field_type))

            self.conn.commit()

        except sqlite3.OperationalError:
            raise UserError

    def create_user(self, username, masterpass):

        try:
            self.add_user_to_master(username, masterpass)
            self.create_user_table(username)

            self.user = User(username, masterpass)
        except UserError:
            print('---user already exists---')

    def login(self, username, password):

        self.cursor.execute("SELECT * FROM USER_DATABASE WHERE USER = ?", (username,))
        row = self.cursor.fetchall()

        try:
            hashed_pass = row[0][1]
            masterpass = self.crypto.decrypt(hashed_pass)

            if masterpass == password:
                print('---login successful---')
                self.user = User(username, password)
            else:
                print('---invalid password---')
        except IndexError:
            print('---user does not exist---')

    def retrieve_table(self):

        self.cursor.execute("SELECT * FROM " + self.user.database)
        table = self.cursor.fetchall()

        for entry in table:
            password = self.crypto.decrypt(entry[2])
            print('Service: ' + entry[0] + ', Username ' + entry[1] + ', Password: ' + password)

    def add_user_entry(self, service, service_username, service_password):

        hashed_pass = self.crypto.encrypt(service_password)

        params = (service, service_username, hashed_pass)
        self.cursor.execute("INSERT INTO " + self.user.database + " (SERVICE, USERNAME, PASSWORD) VALUES (?, ?, ?)", params)

        self.conn.commit()

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
            print('2: add entry')
            print('3: logout')

            commands = {
                '1': self.retrieve_table,
                '2': self.add_user_entry_cmd,
                '3': exit,
            }

            try:
                commands[input()]()
            except KeyError:
                print('---invalid input---')


class UserError(Exception):
    pass
