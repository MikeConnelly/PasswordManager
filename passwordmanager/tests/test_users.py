import unittest
from passwordmanager import app
from passwordmanager.src.password_manager import PasswordManager, UserError
from passwordmanager.src.models import User
from passwordmanager.tests import create_test_env, destroy_test_env


class TestAddAccounts(unittest.TestCase):
    '''
    class docstring
    '''
    def setUp(self):
        create_test_env.init_env()
        paths = app.get_paths('./passwordmanager/tests/data/paths.json')
        self.pm = PasswordManager(paths)

    def test_add_first_user(self):
        self.pm.create_user_and_login('test_user', 'test_pass')
        self.assertIsNotNone(self.pm.user)
        self.assertEqual(self.pm.user.username, 'test_user')
        self.assertEqual(self.pm.crypto.decrypt(self.pm.user.master_password), 'test_pass')

    def test_login(self):
        self.pm.create_user('test_user', 'test_pass')
        self.assertIsNone(self.pm.user)
        self.pm.login('test_user', 'test_pass')
        self.assertIsNotNone(self.pm.user)
        self.assertEqual(self.pm.user.username, 'test_user')

    def test_add_multiple_users(self):
        self.pm.create_user('test_user_1', 'test_pass_1')
        self.pm.create_user('test_user_2', 'test_pass_2')
        self.assertIsNotNone(self.pm.session.query(User).filter(User.username == 'test_user_1'))
        self.assertIsNotNone(self.pm.session.query(User).filter(User.username == 'test_user_2'))

    def test_no_duplicate_users(self):
        self.pm.create_user_and_login('test_user', 'test_pass')
        with self.assertRaises(UserError):
            self.pm.create_user_and_login('test_user', 'any_password')

    def tearDown(self):
        self.pm.logout()
        destroy_test_env.destroy_env()
