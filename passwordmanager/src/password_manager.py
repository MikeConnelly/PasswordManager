import os
import csv
import json
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .crypto import Cipher, get_hashed_password, compare_passwords, generate_key
from .models import Base, Account, User


class PasswordManager:
    """
    class docstring
    """

    def __init__(self, paths):
        self.sqlite_file = paths['database_path']
        self.user = None
        self.crypto = None
        if not os.path.isfile(self.sqlite_file):
            engine = create_engine('sqlite://' + self.sqlite_file)
            Base.metadata.create_all(bind=engine)
        else:
            engine = create_engine('sqlite://' + self.sqlite_file)
            Base.metadata.bind = engine
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.required_fields = ['name', 'email', 'password']

    def create_user(self, username, masterpass, key_path):
        """Adds new user to user_table in database"""
        user_list = self.session.query(User).filter(User.username == username).one_or_none()
        if user_list is not None:
            raise UserError('user already exists')
        else:
            user = User()
            user.username = username
            user.master_password = get_hashed_password(masterpass)
            with open(key_path, 'w') as k:
                k.write(generate_key().decode('utf-8'))
            self.session.add(user)
            self.session.commit()

    def login(self, username, password, key_path):
        """Sets user for current session"""
        query = self.session.query(User).filter(User.username == username)
        user = query.one_or_none()
        if user is None:
            raise UserError('user does not exist')
        hashed_pass = user.master_password
        success, rehash = compare_passwords(password, hashed_pass)
        if not success:
            raise UserError('incorrect password')
        if rehash:
            query.update({'master_password': get_hashed_password(password)})
        with open(key_path, 'r') as k:
            key = k.read()
        self.user = user
        self.crypto = Cipher(key)
        return True

    def create_user_and_login(self, username, masterpass, key_path):
        """Adds new user to database and logs them in"""
        self.create_user(username, masterpass, key_path)
        self.login(username, masterpass, key_path)
        self.add_column('url')

    def retrieve_table(self, decrypt=True):
        """Prints the table of accounts for the current user"""
        table = []
        for account in self.user.accounts:
            email = self.crypto.decrypt(account.email) if decrypt else account.email
            password = self.crypto.decrypt(account.password) if decrypt else account.password
            entry = {
                'name': account.name,
                'email': email,
                'password': password
            }
            if account.expansion:
                expansion = json.loads(account.expansion)
                for field, value in expansion.items():
                    entry[field] = value
            table.append(entry)
        return table

    def add_user_entry(self, account_name, account_email, account_password, custom_cols=None):
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
        columns = self.required_fields
        custom_cols = self.get_custom_columns()
        columns.extend(custom_cols)
        return columns

    def add_column(self, name):
        """Add a column to the user's table of accounts"""
        if ',' in name:
            raise UserError('column names cannot contain ","')
        if name in self.get_all_columns():
            raise UserError(f"column with name {name} already exists")
        custom_cols = self.get_custom_columns()
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
        """Set color field for the given account"""
        query = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)
        account = query.one()
        extras = json.loads(account.extras) if account.extras else {}
        extras['color'] = color
        query.update({'extras': json.dumps(extras)})
        self.session.commit()

    def get_row_color(self, account_name):
        """Get color field for the given account"""
        account = self.session.query(Account)\
                .filter(Account.user_id == self.user.id)\
                .filter(Account.name == account_name)\
                .one()
        extras = json.loads(account.extras) if account.extras else {}
        return extras['color'] if 'color' in extras else None

    def export_to_csv(self, path, decrypt=False):
        """Export account table to a csv file"""
        table = self.retrieve_table(decrypt)
        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.get_all_columns(), extrasaction='ignore', dialect='excel')
            writer.writeheader()
            for account in table:
                writer.writerow(account)

    def import_from_csv(self, path, reset=False, replace_duplicates=False, add_columns=True):
        """Import account table from csv file"""
        if not self.verify_csv(path):
            raise CsvError()
        if reset:
            self.reset_all()
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                account_name = row['name']
                account = self.session.query(Account).filter(Account.name == account_name).one_or_none()
                # check for duplicate
                if account is None or replace_duplicates:
                    if replace_duplicates:
                        self.remove_entry(account_name)
                    custom = {field: value for field, value in row.items() if field not in self.required_fields}
                    for column in custom:
                        if add_columns and column not in self.get_custom_columns():
                            self.add_column(column)
                        else:
                            if column not in self.get_custom_columns():
                                custom.pop(column)
                    self.add_user_entry(row['name'], row['email'], row['password'], custom_cols=custom)

    def verify_csv(self, path):
        """Verifies the format of a csv file before importing"""
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for attr in self.required_fields:
                    if attr not in row:
                        return False
        return True


def generate_password(pass_len):
    """generate random password"""
    chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    password = ''.join(random.sample(chars, pass_len))
    return password


class UserError(Exception):
    """user exception docstring"""


class AccountError(Exception):
    """account exception docstring"""


class CsvError(Exception):
    """exception raised from attempting to import an invalid csv"""
