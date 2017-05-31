import py2neo
import re

from ConfigParser import SafeConfigParser

try:
    import userUtils
except ImportError:
    pass

#Reading from config file
parser = SafeConfigParser()
#with open('../conf/whitelightning.conf') as f:
with open('../conf/whitelightning.conf') as f:
    parser.readfp(f)

DB_SERVER   = parser.get('database', 'url')
DB_USERNAME = parser.get('database', 'username')
DB_PASSWORD = parser.get('database', 'password')

#Flushing out the parser var for security
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

    def queryAll(self, command):
        return self.graph.data(command)

    def queryFirst(self, command):
        results = self.queryAll(command)

        try:
            return results[0]
        except IndexError:
            return ""

def userLogin(username, password, db):
    error = None

    username = userUtils.setUsername(username)
    password = userUtils.setPassword(username, password)

    if not username or not password:
        return "Something phishy is happening"

    user = db.queryFirst("MATCH (u:_USER {username: '%s', password: '%s'}) RETURN u" %(username, password))

    if len(user) == 0:
        error = "Username and password combo do not match"

    return error

def getAllUsers():
    #will clean this up later, just needed it for login purposes
    try:
        graph = py2neo.Graph(DB_SERVER, user=DB_USERNAME, password=DB_PASSWORD)
    except py2neo.Unauthorized:
        return False

    users = {}
    all_users = graph.data("MATCH (u:_USER) RETURN u")
    for user in all_users:
        users[user['u']['username']] = {
            "username" : user['u']['username'],
            "encrypted_password" : user['u']['password'],
            "is_admin" : user['u']['isAdmin'],
            "is_eng" : user['u']['isEng'],
            "is_dev" : user['u']['isDev'],
            "company" : user['u']['company'],
            "job_title" : user['u']['jobTitle'],
            "country" : user['u']['country'],
            "first_name" : user['u']['firstName'],
            "last_name" : user['u']['lastName'],
            "full_name" : userUtils.setFullName(user['u']['firstName'], user['u']['lastName'])   
        }
    
    return users
