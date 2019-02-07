'''
functionality:
 - create table of users and master passwords
 - register users into master table
 - for each user create a table of services/usernames/passwords
 - add entries to user tables
 - authenticate user information to login
 - encrypt information in both tables
 - decrypt and retrieve information
'''
import os.path
import sqlite3


def create_db():

    sqlite_file = 'pmdb.sqlite'
    table_name = 'USER_DATABASE'
    field_1 = 'USER'
    field_2 = 'MASTER_PASSWORD'
    field_type = 'TEXT'

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("CREATE TABLE {tn} ({f1} {ft}, {f2} {ft})"
              .format(tn=table_name, f1=field_1, f2=field_2, ft=field_type))

    conn.commit()
    conn.close()


def add_user_to_master(username, masterpass):

    sqlite_file = 'pmdb.sqlite'

    if not os.path.isfile(sqlite_file):
        create_db()

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    params = (username, masterpass)
    c.execute("INSERT INTO USER_DATABASE (USER, MASTER_PASSWORD) VALUES (?, ?)", params)

    conn.commit()
    conn.close()


def create_user_table(username):

    sqlite_file = 'pmdb.sqlite'
    table_name = username + '_PASSWORD_DATABASE'
    field_1 = 'SERVICE'
    field_2 = 'USERNAME'
    field_3 = 'PASSWORD'
    field_type = 'TEXT'

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("CREATE TABLE {tn} ({f1} {ft}, {f2} {ft}, {f3} {ft})"
              .format(tn=table_name, f1=field_1, f2=field_2, f3=field_3, ft=field_type))

    conn.commit()
    conn.close()


def add_user_info(user, service, service_username, service_password):

    sqlite_file = 'pmdb.sqlite'

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    params = (service, service_username, service_password)
    c.execute("INSERT INTO " + user + "_PASSWORD_DATABASE (SERVICE, USERNAME, PASSWORD) VALUES (?, ?, ?)", params)

    conn.commit()
    conn.close()


def create_user(username, masterpass):

    add_user_to_master(username, masterpass)
    create_user_table(username)


def login(username, password):

    sqlite_file = 'pmdb.sqlite'

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("SELECT * FROM USER_DATABASE WHERE USER = ?", (username,))
    row = c.fetchall()

    if row[0][1] == password:
        pass

    c.close()


def retrieve_table(user):
    pass


if __name__ == '__main__':

    user = 'mike'
    password = 'maspass'

    #create_user(user, password)
    login(user, password)
    retrieve_table(user)
