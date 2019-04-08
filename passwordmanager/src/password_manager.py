import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .crypto import Crypto
from .models import Base, Account, User


class PasswordManager:
    """
    class docstring
    """

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

    def create_user(self, username, masterpass):
        """Adds new user to user_table in database"""

        # check if user already exists, throws error if multiple results
        user_list = self.session.query(User).filter(User.username == username).one_or_none()

        if user_list is not None:
            raise UserError('user already exists')
        else:
            hashed_masterpass = self.crypto.encrypt(masterpass)

            user = User()
            user.username = username
            user.master_password = hashed_masterpass

            self.session.add(user)
            self.session.commit()

    def login(self, username, password):
        """Sets user for current session"""
        user = self.session.query(User).filter(User.username == username).one_or_none()
        if user is None:
            raise UserError('user does not exist')

        hashed_pass = user.master_password
        masterpass = self.crypto.decrypt(hashed_pass)

        if masterpass != password:
            raise UserError('incorrect password')
        self.user = user
        return True

    def create_user_and_login(self, username, masterpass):
        """Adds new user to database and logs them in"""
        self.create_user(username, masterpass)
        self.login(username, masterpass)

    def retrieve_table(self):
        """Prints the table of accounts for the current user"""
        table = []
        for account in self.user.accounts:
            entry = {
                'name': account.name,
                'email': self.crypto.decrypt(account.email),
                'password': self.crypto.decrypt(account.password),
                'url': account.url
            }
            if account.expansion:
                expansion = json.loads(account.expansion)
                for field, value in expansion.items():
                    entry[field] = value
            table.append(entry)
        return table

    def add_user_entry(self, account_name, account_email, account_password, account_url='', custom_cols=None):
        """Add an account to the current user's table"""

        row = self.session.query(Account)\
            .filter(Account.user_id == self.user.id)\
            .filter(Account.name == account_name)\
            .one_or_none()
        if row is not None:
            raise AccountError(f"account with name {account_name} already exists")

        hashed_pass = self.crypto.encrypt(account_password)
        hashed_email = self.crypto.encrypt(account_email)

        account = Account()
        account.name = account_name
        account.email = hashed_email
        account.password = hashed_pass
        account.url = account_url
        account.user_id = self.user.id
        if custom_cols:
            account.expansion = json.dumps(custom_cols)

        self.session.add(account)
        self.session.commit()

    def remove_entry(self, account):
        """Removes an account from the current user's table"""
        row = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account['name'])\
                .one()
        self.session.delete(row)
        self.session.commit()

    def change_entry(self, account, col, new_field):
        """Changes a field in an account"""
        if col == 'name':
            if self.session.query(Account)\
                    .filter(Account.user_id == self.user.id)\
                    .filter(Account.name == new_field)\
                    .one_or_none() is not None:
                raise AccountError(f"account with name {new_field} already exists")
        elif col == 'email' or col == 'password':
            new_field = self.crypto.encrypt(new_field)
        elif col in self.user.custom_cols.split(','):
            query = self.session.query(Account)\
                    .filter(Account.user_id == self.user.id)\
                    .filter(Account.name == account['name'])\
                    .one()
            expansion = json.loads(query.expansion) if query.expansion else {}
            expansion[col] = new_field
            col = 'expansion'
            new_field = json.dumps(expansion)

        self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account['name'])\
                .update({col: new_field})
        self.session.commit()

    def add_column(self, name):
        """Add a column to the user's table of accounts"""
        if ',' in name:
            raise UserError('column names cannot contain ","')
        custom_cols = self.user.custom_cols.split(',') if self.user.custom_cols else []
        if name in custom_cols:
            raise UserError(f"column with name {name} already exists")
        custom_cols.append(name)
        cols_str = ','.join(custom_cols)
        self.session.query(User).filter(User.id == self.user.id).update({'custom_cols': cols_str})
        self.session.commit()

    def logout(self):
        """Removes user and closes database session"""
        self.user = None
        self.session.close()

    def get_all_columns(self):
        """Returns all the user's required and custom fields"""
        all_fields = ['name', 'email', 'password', 'url']
        custom_cols = self.user.custom_cols.split(',') if self.user.custom_cols else []
        all_fields.extend(custom_cols)
        return all_fields


class UserError(Exception):
    """user exception docstring"""


class AccountError(Exception):
    """account exception docstring"""
