

class User:

    def __init__(self, username, password):

        self.username = username
        self.password = password
        self.database = username + '_PASSWORD_DATABASE'
