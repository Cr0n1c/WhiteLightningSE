import re
import uuid

import bcrypt as bcrypt


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
        self.full_name = '%s %s' % (self.first_name, self.last_name)
        self.uuid = ""

    def run_error_checker(self):
        if not self.is_password_encrypted():
            return False

        self.username = set_username(self.username)
        self.state = set_state(self.state)
        self.country = set_country(self.country)
        self.email = set_email(self.email)
        self.first_name = set_name(self.first_name)
        self.last_name = set_name(self.last_name)
        self.full_name = set_full_name(self.first_name, self.last_name)

        for k in [self.is_admin, self.is_eng, self.is_dev]:
            if k not in ["true", "false"]:
                return False

        if self.username is False or self.email is False or self.country is False:
            return False
        else:
            return True

    def is_password_encrypted(self):
        if self.encrypted_password is None:
            return False

        if re.match("^[a-f0-9]{128}$", self.encrypted_password):
            return True
        else:
            return False


class NewUser(object):
    def __init__(self, request_form):
        self.username = set_username(request_form['username'])
        # TODO (ecolq): Fix the code paths to get to here. The password is encrypted already, but maybe should be
        # delegated to this point?
        self.encrypted_password = set_password(request_form['password'])
        self.job_title = request_form['job']
        self.state = set_state(request_form['state'])
        self.country = set_country(request_form['country'])
        self.department = request_form['department']
        self.email = set_email(request_form['email'])
        self.first_name = set_name(request_form['firstname'])
        self.last_name = set_name(request_form['lastname'])
        self.full_name = set_full_name(self.first_name, self.last_name)
        self.is_admin = self.set_priv_status(request_form, 'role_adm')
        self.is_eng = self.set_priv_status(request_form, 'role_eng')
        self.is_dev = self.set_priv_status(request_form, 'role_dev')

    def set_priv_status(self, d, k):
        # TODO (ecolq): This looks flawed - shouldn't we take the role if it exists, else false?
        try:
            d[k]
        except KeyError:
            return "false"
        else:
            return "true"


def set_uuid(username):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, username))


def set_full_name(first_name, last_name):
    first = set_name(first_name)
    last = set_name(last_name)
    return ' '.join(filter(None, (first, last)))


def set_name(name):
    # set to match rules in static/js/gsdk-bootstrap-wizard.js
    if name is None:
        return ""

    name = name.strip()
    if len(name) < 3:
        return ""

    if len(name) > 20:
        return False

    if not re.match("^[A-Za-z]{3,20}$", name):
        return False

    # passed all checks, now formatting it
    # TODO (ecolq): Can we swap with with name.capitalise()?
    first_letter = name[0].upper()
    rest_of_name = name[1:].lower()
    return first_letter + rest_of_name


def set_username(username):
    # TODO (ecolq): Change the minimum username length on the front end to 5.
    # The default neo4j username (neo4j) is too short.
    # set to match rules in static/js/gsdk-bootstrap-wizard.js
    if username is None:
        return False

    username = username.strip()
    if len(username) < 5 or len(username) > 15:
        return False
    elif not re.match("^[A-Za-z0-9_]{5,15}$", username):
        return False

    # passed all the checks, now formatting it
    return username.lower()


def set_password(password):
    # set to match rules in static/js/gsdk-bootstrap-wizard.js
    if password is None:
        return False
    elif len(password) < 7 or len(password) > 20:
        return False
    elif not re.match("^[^'\"\\s]+$", password):
        return False

    # passed all the checks, now formatting it
    password = password.strip().encode('utf-8')
    encrypted_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return encrypted_password


def set_state(state):
    if state is None or state.strip() == "":
        return ""
    return state.strip().split(" ")[0]


def set_country(country):
    if country is None:
        return ""
    return country.strip()


def set_email(email):
    # set to match rules in static/js/gsdk-bootstrap-wizard.js
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

    # passed all the checks, now formatting it
    return email.lower()
