'''
to-do:
 - create a file that holds the directories of key and db for different users
 - use absolute file paths for simplicity
'''
from .crypto import Crypto
from .models import Base, Account, User
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
        '''
        Adds new user to user_table in database
        '''

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
        '''
        Sets user for current session
        '''

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
        '''
        Adds new user to database and logs them in
        '''

        try:
            self.add_user_to_master(username, masterpass)
            self.login(username, masterpass)
        except UserError:
            print('---user already exists---')

    def retrieve_table(self):
        '''
        Prints the table of accounts for the current user
        '''

        table = []
        for account in self.user.accounts:
            entry = {
                'name': account.name,
                'email': account.email,
                'url': account.url,
                'password': self.crypto.decrypt(account.password)
            }
            table.append(entry)
        
        return table

    def add_user_entry(self, account_name, account_email, account_password):
        '''
        Add an account to the current user's table
        '''

        hashed_pass = self.crypto.encrypt(account_password)

        account = Account()
        account.name = account_name
        account.email = account_email
        account.password = hashed_pass
        account.user_id = self.user.id

        self.session.add(account)
        self.session.commit()

    def remove_entry(self, entry):
        '''
        Removes an account from the current user's table
        '''

        self.session.delete(entry)
        self.session.commit()

    def change_entry(self, entry, field, new_field):
        '''
        Changes a field in an account
        '''

        self.session.query(Account).filter(Account.id == entry.id).update({entry: new_field})
        self.session.commit()

    def logout(self):
        '''
        Closes database session and ends the exits the program
        '''

        self.session.close()
        exit(0)


class UserError(Exception):
    pass
