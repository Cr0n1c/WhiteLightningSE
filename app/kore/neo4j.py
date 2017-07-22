import bcrypt
import os
import requests

from ConfigParser import SafeConfigParser

import py2neo

import user_utils

from __init__ import load_config

# Reading from config file
parser = load_config()
if not parser:
    DB_SERVER = "127.0.0.1"
    DB_USERNAME = "neo4j"
    DB_PASSWORD = "neo4j"
    PARSER_DETECTED = False
else:
    DB_SERVER = parser.get('database', 'url')
    DB_USERNAME = parser.get('database', 'username')
    DB_PASSWORD = parser.get('database', 'password')
    PARSER_DETECTED = True

# Flushing out the parser var for security
parser = None


class Initialize(object):
    def __init__(self, username=DB_USERNAME, password=DB_PASSWORD):
        if not self.set_creds():
            self.username = username
            self.password = password
        self.connect(self.username, self.password)

    def __del__(self):
        self.username = None
        self.password = None
        self.graph = None

    def set_creds(self):
        if not PARSER_DETECTED:
            parser = load_config()
            if parser is False:
                return False
            else:
                self.username = parser.get('database', 'username')
                self.password = parser.get('database', 'password')
                return True
        
        return False

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


def change_db_password(current_password, new_password):
    headers = {'Content-Type': 'application/json', }
    data = '{"password":"' + new_password + '"}'
    resp = requests.post('http://localhost:7474/user/neo4j/password', headers=headers, data=data, auth=('neo4j', current_password))
    return resp.status_code

def user_login(username, password, db):
    print username
    print password
    
    error = None

    formatted_username = user_utils.set_username(username)

    if not formatted_username:
        return "Something phishy is happening"

    user = db.query_first("MATCH (u:_USER {username: '%s'}) RETURN u" %
                          (formatted_username))
   
    try:
        print "\t password : " + password
        print "\t bcrypt_password: " + bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print "\t db password: " + user["u"]["password"]

        if len(user) == 0 or not bcrypt.checkpw(password.encode('utf-8'), user["u"]["password"].encode('utf-8')):
            error = "Username and password combo do not match"
    except ValueError:
        error = "Database password is jacked up for this user"
    
    print "---------------------------"
    print error
    print "---------------------------"
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
