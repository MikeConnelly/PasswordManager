'''
functionality:
 - create table of users and master passwords
 - register users into master table
 - for each user create a table of services/usernames/passwords
 - add entries to user tables
 - authenticate user information to login
 - encrypt information in both tables
 - decrypt and retrieve information
'''
import sys
import os.path
import sqlite3
from .user import User


class PasswordManager:

    def __init__(self):

        self.sqlite_file = 'pmdb.sqlite'

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

        params = (username, masterpass)
        self.cursor.execute("INSERT INTO USER_DATABASE (USER, MASTER_PASSWORD) VALUES (?, ?)", params)

        self.conn.commit()

    def create_user_table(self, username):

        table_name = username + '_PASSWORD_DATABASE'
        field_1 = 'SERVICE'
        field_2 = 'USERNAME'
        field_3 = 'PASSWORD'
        field_type = 'TEXT'

        self.cursor.execute("CREATE TABLE {tn} ({f1} {ft}, {f2} {ft}, {f3} {ft})"
                  .format(tn=table_name, f1=field_1, f2=field_2, f3=field_3, ft=field_type))

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

    def create_user(self, username, masterpass):

        self.add_user_to_master(username, masterpass)
        self.create_user_table(username)

        self.user = User(username, masterpass)

    def login_cmd(self):

        print('Enter username: ')
        username = input()
        print('Enter password: ')
        password = input()

        self.login(username, password)

    def login(self, username, password):

        self.cursor.execute("SELECT * FROM USER_DATABASE WHERE USER = ?", (username,))
        row = self.cursor.fetchall()

        if row[0][1] == password:
            print('login successful')
        else:
            print('invalid password')

        self.user = User(username, password)

    def retrieve_table(self, user):

        self.cursor.execute("SELECT * FROM " + user + "_PASSWORD_DATABASE")
        table = self.cursor.fetchall()

        user.fill_table(table)
        print(table)

    def add_user_entry_cmd(self):

        print('Service: ')
        service = input()

        print('Username: ')
        username = input()

        print('Password: ')
        password = input()

        self.add_user_entry(self.user, service, username, password)

    def add_user_entry(self, user, service, service_username, service_password):

        params = (service, service_username, service_password)
        self.cursor.execute("INSERT INTO " + user + "_PASSWORD_DATABASE (SERVICE, USERNAME, PASSWORD) VALUES (?, ?, ?)", params)

        self.conn.commit()

    def get_user_command(self):

        print('1: retrieve table')
        print('2: add entry')
        print('3: logout')

        commands = {
            1: self.retrieve_table,
            2: self.add_user_entry_cmd,
            3: exit,
        }

        commands[input()]()


if __name__ == '__main__':

    pm = PasswordManager()

    command = sys.argv[1]

    if command == 'newuser':
        pm.create_user_cmd()
    elif command == 'login':
        pm.login_cmd()
    else:
        print('invalid command')

    pm.get_user_command()
