'''
create/destroy test env
To test:
 - test main (pass in path file arg)
 - data folder is created
 - sqlite file and key are created
 - accounts can be added and retrieved
 - accounts can be removed
 - all fields can be changed
 - all key errors are caught?
 - database and key dirs can be changed
'''

import unittest
import sys
import main
from main import get_paths
from passwordmanager import password_manager
from passwordmanager import models
import tests
from tests import create_test_env, destroy_test_env
from create_test_env import init_env
from destroy_test_env import destroy_env
import time
# sys.path.append(sys.path[0])


class TestUsers(unittest.TestCase):

    def add_user(self):

        self.assertTrue(init_env())
        paths = get_paths('./tests/docs/paths.txt')
        pm = password_manager.PasswordManager(paths)

        pm.add_user_to_master('user1', 'password1')
        user = pm.session.query(models.User).filter(models.User.username == 'user1').one()
        self.assertEquals(user.username, 'user1')
        self.assertEquals(pm.crypto.decrypt(user.master_password), 'password1')

        pm.session.close()
        destroy_env()
