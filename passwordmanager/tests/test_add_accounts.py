import unittest
from passwordmanager import app
from passwordmanager.src import password_manager, models
from passwordmanager.tests import create_test_env, destroy_test_env


class TestAddAccounts(unittest.TestCase):
    def setUp(self):
        print('setup TestAddAccounts')
        create_test_env.init_env()
        paths = app.get_paths('./passwordmanager/tests/docs/paths.txt')
        self.pm = password_manager.PasswordManager(paths)

    def test(self):
        print('testing')
        assert(self.pm)

    def tearDown(self):
        print('teardown TestAddAccounts')
        self.pm.close_session()
        destroy_test_env.destroy_env()
'''
add a logout_cmd in interface that exits program
remove exit(0) from pm.logout
call logout over close_session()
C:\Users\Mike\Envs\pmenv\Scripts\pyuic5.exe
'''