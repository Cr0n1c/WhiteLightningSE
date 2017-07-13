import bcrypt
import os
from ConfigParser import SafeConfigParser

import py2neo

import user_utils

# Reading from config file
parser = SafeConfigParser()
with open(os.path.join(os.getcwd(), "..", "conf", "whitelightning.conf")) as f:
    parser.readfp(f)

DB_SERVER = parser.get('database', 'url')
DB_USERNAME = parser.get('database', 'username')
DB_PASSWORD = parser.get('database', 'password')

# Flushing out the parser var for security
parser = None


class Initialize(object):
    def __init__(self, username=DB_USERNAME, password=DB_PASSWORD):
        self.username = username
        self.password = password
        self.connect(self.username, self.password)

    def __del__(self):
        self.username = None
        self.password = None
        self.graph = None

    def connect(self, username, password):
        try:
            self.graph = py2neo.Graph(DB_SERVER, user=username, password=password)
        except py2neo.Unauthorized:
            self.connected = False
        else:
            self.connected = True

    def query_all(self, command):
        return self.graph.data(command)

    def query_first(self, command):
        results = self.query_all(command)

        try:
            return results[0]
        except IndexError:
            return ""


def user_login(username, password, db):
    error = None

    formatted_username = user_utils.set_username(username)
    encrypted_password = user_utils.set_password(password)

    if not formatted_username or not encrypted_password:
        return "Something phishy is happening"

    user = db.query_first("MATCH (u:_USER {username: '%s'}) RETURN u" %
                          (formatted_username))
   
    try:
        if len(user) == 0 or not bcrypt.checkpw(password.encode('utf-8'), user["u"]["password"].encode('utf-8')):
            error = "Username and password combo do not match"
    except ValueError:
        error = "Database password is jacked up for this user"
    return error


def get_all_users():
    try:
        graph = py2neo.Graph(DB_SERVER, user=DB_USERNAME, password=DB_PASSWORD)
    except py2neo.Unauthorized:
        return False

    users = {}
    all_users = graph.data("MATCH (u:_USER) RETURN u")
    for user in all_users:
        users[user['u']['username']] = {
            "username": user['u']['username'],
            "encrypted_password": user['u']['password'],
            "is_admin": user['u']['isAdmin'],
            "is_eng": user['u']['isEng'],
            "is_dev": user['u']['isDev'],
            "company": user['u']['company'],
            "job_title": user['u']['jobTitle'],
            "country": user['u']['country'],
            "first_name": user['u']['firstName'],
            "last_name": user['u']['lastName'],
            "full_name": user_utils.set_full_name(user['u']['firstName'], user['u']['lastName'])
        }

    return users
