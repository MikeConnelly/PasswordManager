import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .crypto import Crypto
from .models import Base, Account, User


class PasswordManager:
    '''
    class docstring
    '''
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
        '''Adds new user to user_table in database'''

        # check if user already exists
        user_list = self.session.query(User).filter(User.username == username).all()

        if user_list != []:
            raise UserError('user already exists')
        else:
            hashed_masterpass = self.crypto.encrypt(masterpass)

            user = User()
            user.username = username
            user.master_password = hashed_masterpass

            self.session.add(user)
            self.session.commit()

    def login(self, username, password):
        '''Sets user for current session'''
        try:
            user = self.session.query(User).filter(User.username == username).one()
        except NoResultFound:
            raise UserError('user does not exist')

        hashed_pass = user.master_password
        masterpass = self.crypto.decrypt(hashed_pass)

        if masterpass != password:
            raise UserError('incorrect password')
        self.user = user
        return True

    def create_user(self, username, masterpass):
        '''Adds new user to database and logs them in'''
        self.add_user_to_master(username, masterpass)
        self.login(username, masterpass)

    # call this function from __init__ and use a class variable to call from interfaces
    def retrieve_table(self):
        '''Prints the table of accounts for the current user'''
        table = []
        for account in self.user.accounts:
            entry = {
                'id': account.id,
                'name': account.name,
                'email': self.crypto.decrypt(account.email),
                'password': self.crypto.decrypt(account.password),
                'url': account.url
            }
            table.append(entry)
        return table

    def add_user_entry(self, account_name, account_email, account_password, account_url=''):
        '''Add an account to the current user's table'''

        # check if account already exists
        row = self.session.query(Account)\
            .filter(Account.user_id == self.user.id)\
            .filter(Account.name == account_name)\
            .all()
        if row != []:
            raise AccountError(f"account with name {account_name} already exists")

        hashed_pass = self.crypto.encrypt(account_password)
        hashed_email = self.crypto.encrypt(account_email)

        account = Account()
        account.name = account_name
        account.email = hashed_email
        account.password = hashed_pass
        account.url = account_url
        account.user_id = self.user.id

        self.session.add(account)
        self.session.commit()

    def remove_entry(self, account):
        '''Removes an account from the current user's table'''
        row = self.session.query(Account).filter(Account.id == account['id']).one()
        self.session.delete(row)
        self.session.commit()

    def change_entry(self, account, col, new_field):
        '''Changes a field in an account'''
        if col == 'email' or col == 'password':
            new_field = self.crypto.encrypt(new_field)
        
        self.session.query(Account).filter(Account.id == account['id']).update({col: new_field})
        self.session.commit()

    def logout(self):
        '''Removes user and closes database session'''
        self.user = None
        self.session.close()


class UserError(Exception):
    '''user exception docstring'''


class AccountError(Exception):
    '''account exception docstring'''
