import hashlib
import re
import uuid

class UserInformation(object):

    def __init__(self):
        self.company = ""
        self.job_title = ""
        self.country = ""
        self.state = ""
        self.email = ""
        self.encrypted_password = None
        self.username = None
        self.profile_pic = None
        self.first_name = ""
        self.last_name = ""
        self.is_admin = "false"
        self.is_eng = "false"
        self.is_dev = "false"
        self.full_name = '%s %s' %(self.first_name, self.last_name)
        self.uuid = ""

    def runErrorChecker(self):
        if not self.isPasswordEncrypted():
            return False

        self.username = setUsername(self.username)
        self.state = setState(self.state)
        self.country = setCountry(self.country)
        self.email = setEmail(self.email)
        self.first_name = setName(self.first_name)
        self.last_name = setName(self.last_name)
        self.full_name = setFullName(self.first_name, self.last_name)

        for k in [self.is_admin, self.is_eng, self.is_dev]:
            if k not in ["true", "false"]:
                return False

        if self.username is False or self.email is False or self.country is False:
            return False
        else:
            return True

    def isPasswordEncrypted(self):
        if self.encrypted_password is None:
            return False

        if re.match("^[a-f0-9]{128}$", self.encrypted_password):
            return True
        else:
            return False

class NewUser(object):

    def __init__(self, request_form):
        self.username = setUsername(request_form['username'])
        self.encrypted_password = setPassword(self.username, request_form['password'])
        self.job_title = request_form['job']
        self.state = setState(request_form['state'])
        self.country = setCountry(request_form['country'])
        self.department = request_form['department']
        self.email = setEmail(request_form['email'])
        self.first_name = setName(request_form['firstname'])
        self.last_name = setName(request_form['lastname'])
        self.full_name = setFullName(self.first_name, self.last_name)
        self.is_admin = self.setPrivStatus(request_form, 'role_adm')
        self.is_eng = self.setPrivStatus(request_form, 'role_eng')
        self.is_dev = self.setPrivStatus(request_form, 'role_dev')

    def setPrivStatus(self, d, k):
        try:
            d[k]
        except KeyError:
            return "false"
        else:
            return "true"


def setUUID(username):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, username))

def setFullName(first_name, last_name):
    first = setName(first_name)
    last = setName(last_name)
    if not first:
        first = ""

    if not last:
        last = ""
    return "%s %s" %(first, last)

def setName(name):
    #set to match rules in static/js/gsdk-bootstrap-wizard.js
    if name is None:
        return ""

    name = name.strip()
    if len(name) < 3:
        return ""

    if len(name) > 20:
        return False

    if not re.match("^[A-Za-z]{3,20}$", name):
        return False

    #passed all checks, now formatting it
    first_letter = name[0].upper()
    rest_of_name = name[1:].lower()
    return first_letter + rest_of_name

def setUsername(username):
    #set to match rules in static/js/gsdk-bootstrap-wizard.js
    if username is None:
        return False

    username = username.strip()
    if len(username) < 6 or len(username) > 15:
        return False
    elif not re.match("^[A-Za-z0-9_]{6,15}$", username):
        return False

    #passed all the checks, now formatting it
    return username.lower()

def setPassword(seed, password, use_seed = True):
    #set to match rules in static/js/gsdk-bootstrap-wizard.js
    if password is None:
        return False
    elif len(password) < 7 or len(password) > 20:
        return False
    elif not re.match("^[^'\"\\s]{1,}$", password):
        return False

    #passed all the checks, now formatting it
    password = password.strip()
    if use_seed:
        encrypted_password = hashlib.sha512(seed + password).hexdigest()
        return encrypted_password
    else:
        return password

def setState(state):
    if state is None or state.strip() == "":
        return ""
    return state.strip().split(" ")[0]

def setCountry(country):
    if country is None:
        return ""
    return country.strip()

def setEmail(email):
    #set to match rules in static/js/gsdk-bootstrap-wizard.js
    if email is None:
        return ""

    email = email.strip()
    if len(email) > 254 or len(email) < 3:
        return False

    email_parts = email.split("@")
    if len(email_parts) != 2:
        return False

    for part in email_parts:
        if not re.match("^[A-Za-z0-9._-]{1,}$", part):
            return False

    #passed all the checks, now formatting it
    return email.lower()


