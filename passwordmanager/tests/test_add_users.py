import unittest
from passwordmanager import app
from passwordmanager.src import password_manager
from passwordmanager.src.models import User
from passwordmanager.tests import create_test_env, destroy_test_env


class TestAddAccounts(unittest.TestCase):
    def setUp(self):
        print('setup TestAddAccounts')
        create_test_env.init_env()

    def test(self):
        print('test users')
        paths = app.get_paths('./passwordmanager/tests/docs/paths.txt')
        pm = password_manager.PasswordManager(paths)

        pm.create_user('user1', 'pass1')
        assert(pm.user.username == 'user1')
        q = pm.session.query(User).filter(User.username == 'user1').one()
        assert(q.master_password == 'pass1')
        pm.close_session()

    def tearDown(self):
        print('teardown TestAddAccounts')
        destroy_test_env.destroy_env()
