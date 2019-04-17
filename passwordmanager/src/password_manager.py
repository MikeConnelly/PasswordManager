import os
import json
import random
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

    def remove_entry(self, account_name):
        """Removes an account from the current user's table"""
        row = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)\
                .one()
        self.session.delete(row)
        self.session.commit()

    def change_entry(self, account_name, cols, new_fields):
        """Changes multiple fields in accounts"""
        account_id = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)\
                .one()\
                .id
        query = self.session.query(Account).filter(Account.id == account_id)
        account = query.one()
        for col, new_field in zip(cols, new_fields):
            update_col, update_field = (col, new_field)
            if col == 'name':
                if self.session.query(Account)\
                        .filter(Account.user_id == self.user.id)\
                        .filter(Account.name == new_field)\
                        .one_or_none() is not None:
                    raise AccountError(f"account with name {new_field} already exists")
            elif col in ('email', 'password'):
                update_field = self.crypto.encrypt(new_field)
            elif col in self.get_custom_columns():
                expansion = json.loads(account.expansion) if account.expansion else {}
                expansion[col] = new_field
                update_col = 'expansion'
                update_field = json.dumps(expansion)
            query.update({update_col: update_field})
        self.session.commit()

    def get_custom_columns(self):
        """Returns the user's custom fields"""
        custom_cols = self.user.custom_cols.split(',') if self.user.custom_cols else []
        return custom_cols

    def get_all_columns(self):
        """Returns all the user's required and custom fields"""
        required_fields = ['name', 'email', 'password', 'url']
        custom_cols = self.get_custom_columns()
        required_fields.extend(custom_cols)
        return required_fields

    def add_column(self, name):
        """Add a column to the user's table of accounts"""
        if ',' in name:
            raise UserError('column names cannot contain ","')
        custom_cols = self.get_custom_columns()
        if name in custom_cols:
            raise UserError(f"column with name {name} already exists")
        custom_cols.append(name)
        cols_str = ','.join(custom_cols)
        self.session.query(User).filter(User.id == self.user.id).update({'custom_cols': cols_str})
        self.session.commit()

    def remove_column(self, name):
        """Remove a column from the user's custom columns"""
        custom_cols = self.get_custom_columns()
        custom_cols.remove(name)
        cols_str = ','.join(custom_cols)
        self.session.query(User).filter(User.id == self.user.id).update({'custom_cols': cols_str})
        self.session.commit()
        # Remove column data from all the user's accounts
        for account in self.user.accounts:
            if account.expansion and name in account.expansion:
                expansion = json.loads(account.expansion)
                expansion.pop(name)
                expansion = json.dumps(expansion)
                self.session.query(Account)\
                        .filter(Account.user_id == self.user.id)\
                        .filter(Account.name == account.name)\
                        .update({'expansion': expansion})
                self.session.commit()

    def rename_column(self, name, new_name):
        """Rename a custom column"""
        custom_cols = self.get_custom_columns()
        index = custom_cols.index(name)
        custom_cols[index] = new_name
        col_str = ','.join(custom_cols)
        self.session.query(User).filter(User.id == self.user.id).update({'custom_cols': col_str})
        # Rename column in all accounts
        for account in self.user.accounts:
            if account.expansion and name in account.expansion:
                expansion = json.loads(account.expansion)
                expansion[new_name] = expansion.pop(name)
                expansion = json.dumps(expansion)
                self.session.query(Account)\
                        .filter(Account.user_id == self.user.id)\
                        .filter(Account.name == account.name)\
                        .update({'expansion': expansion})
                self.session.commit()

    def reset_all(self):
        """Remove all user accounts and reset custom columns"""
        self.session.query(User).filter(User.id == self.user.id).update({'custom_cols': ''})
        self.session.commit()
        for account in self.user.accounts:
            query = self.session.query(Account)\
                    .filter(Account.user_id == self.user.id)\
                    .filter(Account.name == account.name)\
                    .one()
            self.session.delete(query)
            self.session.commit()

    def logout(self):
        """Removes user and closes database session"""
        self.user = None
        self.session.close()

    def color_row(self, account_name, color):
        query = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)
        account = query.one()
        extras = json.loads(account.extras) if account.extras else {}
        extras['color'] = color
        query.update({'extras': json.dumps(extras)})
        self.session.commit()

    def get_row_color(self, account_name):
        account = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)\
                .one()
        extras = json.loads(account.extras) if account.extras else {}
        return extras['color'] if 'color' in extras else None


def generate_password(pass_len):
    """generate random password of length pass_len"""
    chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    password = ''.join(random.sample(chars, pass_len))
    return password


class UserError(Exception):
    """user exception docstring"""


class AccountError(Exception):
    """account exception docstring"""
