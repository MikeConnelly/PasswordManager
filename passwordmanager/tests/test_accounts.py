import unittest
from passwordmanager import app
from passwordmanager.src.password_manager import PasswordManager, AccountError
from passwordmanager.src.models import Account
from passwordmanager.tests import create_test_env, destroy_test_env


class TestAddAccounts(unittest.TestCase):
    '''
    class docstring
    '''
    def setUp(self):
        create_test_env.init_env()
        paths = app.get_paths('./passwordmanager/tests/data/paths.json')
        self.pm = PasswordManager(paths)
        self.pm.add_user_to_master('test_user_1', 'test_pass_1')
        self.pm.add_user_to_master('test_user_2', 'test_pass_2')

    def test_add_account(self):
        self.pm.login('test_user_1', 'test_pass_1')
        self.pm.add_user_entry('account', 'email', 'password')
        query = self.pm.session.query(Account)\
            .filter(Account.user_id == self.pm.user.id)\
            .filter(Account.name == 'account')\
            .all()
        self.assertEqual(len(query), 1)
        result = query[0]
        self.assertEqual(result.name, 'account')
        self.assertEqual(self.pm.crypto.decrypt(result.email), 'email')
        self.assertEqual(self.pm.crypto.decrypt(result.password), 'password')
        self.assertEqual(result.url, '')

    def test_add_multple_accounts(self):
        self.pm.login('test_user_1', 'test_pass_1')
        self.pm.add_user_entry('account1', 'email1', 'password1')
        self.pm.add_user_entry('account2', 'email2', 'password2', 'url2')
        self.pm.add_user_entry('account3', 'email3', 'password3')
        results = self.pm.session.query(Account).filter(Account.user_id == self.pm.user.id).all()
        self.assertEqual(len(results), 3)
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        self.assertEqual(result1.name, 'account1')
        self.assertEqual(self.pm.crypto.decrypt(result1.email), 'email1')
        self.assertEqual(self.pm.crypto.decrypt(result1.password), 'password1')
        self.assertEqual(result1.url, '')
        self.assertEqual(result2.name, 'account2')
        self.assertEqual(self.pm.crypto.decrypt(result2.email), 'email2')
        self.assertEqual(self.pm.crypto.decrypt(result2.password), 'password2')
        self.assertEqual(result2.url, 'url2')
        self.assertEqual(result3.name, 'account3')
        self.assertEqual(self.pm.crypto.decrypt(result3.email), 'email3')
        self.assertEqual(self.pm.crypto.decrypt(result3.password), 'password3')
        self.assertEqual(result3.url, '')

    def test_no_duplicate_accounts(self):
        self.pm.login('test_user_1', 'test_pass_1')
        self.pm.add_user_entry('account', 'email', 'password')
        with self.assertRaises(AccountError):
            self.pm.add_user_entry('account', 'any_email', 'any_password', 'any_url')

    def test_multiple_users_add_accounts(self):
        self.pm.login('test_user_1', 'test_pass_1')
        self.pm.add_user_entry('account', 'email', 'password', 'url')
        id1 = self.pm.user.id
        self.pm.login('test_user_2', 'test_pass_2')
        self.pm.add_user_entry('account', 'email', 'password', 'url')
        id2 = self.pm.user.id
        self.assertEqual(len(self.pm.session.query(Account).filter(Account.user_id == id1).all()), 1)
        self.assertEqual(len(self.pm.session.query(Account).filter(Account.user_id == id2).all()), 1)

    def tearDown(self):
        self.pm.logout()
        destroy_test_env.destroy_env()
