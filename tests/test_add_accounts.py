import unittest
from src import password_manager, models
from tests import create_test_env, destroy_test_env
import main


class TestAddAccounts(unittest.TestCase):
    def setUp(self):
        print('setup TestAddAccounts')
        create_test_env.init_env()

    def test(self):
        print('testing')
        paths = main.get_paths('./tests/docs/paths.txt')
        pm = password_manager.PasswordManager(paths)

    def tearDown(self):
        print('teardown TestAddAccounts')
        destroy_test_env.destroy_env()
