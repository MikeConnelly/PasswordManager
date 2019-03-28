import unittest
from passwordmanager import app
from passwordmanager.src.password_manager import PasswordManager, UserError
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
        self.pm.create_user('test_user1', 'test_pass1')
        self.assertIsNotNone(self.pm.user)
        self.assertEqual(self.pm.user.username, 'test_user1')
        self.assertEqual(self.pm.crypto.decrypt(self.pm.user.master_password), 'test_pass1')

    def test_add_duplicate_user(self):
        self.assertRaises(UserError, self.pm.create_user, 'test_user1', 'different_password')

    def tearDown(self):
        self.pm.logout()
        destroy_test_env.destroy_env()
