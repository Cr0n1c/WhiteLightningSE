import json
import os

import urllib3

from ConfigParser import SafeConfigParser

import neo4j
import query
import template_login
import template_user_control_panel
import template_website_template
import user_utils

urllib3.disable_warnings()

WHITELIGHTNING_CONF_FILE = os.path.join(os.getcwd(), "..", "conf", "whitelightning.conf")

def load_config():
    if not os.path.isfile(WHITELIGHTNING_CONF_FILE):
        return False

    parser = SafeConfigParser()
    with open(WHITELIGHTNING_CONF_FILE) as f:
        parser.readfp(f)

    return parser


def first_run(request_form):
    resp = neo4j.change_db_password("neo4j", request_form["dbpassword"])
    if resp != 200:
        return json.dumps({'success': False}), resp, {'ContentType': 'application/json'}

    try:
        # TODO(ecolq): Encrypt as many of these creds as possible and store in neo4j. See Issue #36
        db_server, none = validate_server(request_form["dbserver"], None, "neo4j")
        db_username = user_utils.set_username(request_form["dbusername"])
        db_password = request_form["dbpassword"]

        ui_username = user_utils.set_username(request_form["uiusername"])
        ui_password = request_form["uipassword"]

        (empire_server, empire_port) = validate_server(request_form["empireserver"], request_form["empireport"])
        empire_username = user_utils.set_username(request_form["empireusername"])
        empire_password = request_form["empirepassword"]

        recaptcha_site_key = validate_re_captcha(request_form["recaptchasite"])
        recaptcha_secret_key = validate_re_captcha(request_form["recaptchasecret"])
    except KeyError:
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}

    # TODO (ecolq): Add password validation here
    # validate_pass(db_password) and
    # validate_pass(ui_password) and
    # validate_pass(empire_password) and
    if validate_server(db_server, None, "neo4j") and \
            user_utils.set_username(db_username) and \
            validate_server(empire_server, empire_port) and \
            user_utils.set_username(empire_username) and \
            ui_username and \
            ui_password and \
            validate_re_captcha_keys(recaptcha_site_key, recaptcha_secret_key):
        pass
    else:
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}

    # Build INI file
    newline = "\n"
    with open(WHITELIGHTNING_CONF_FILE, "w") as f:
        f.write("[server]" + newline)
        f.write("ip = 0.0.0.0" + newline)
        f.write("port = 80" + newline)
        f.write(newline)
        f.write("[database]" + newline)
        f.write("url = " + db_server + newline)
        f.write("username = " + db_username + newline)
        f.write("password = " + db_password + newline)
        f.write(newline)
        f.write("[empirerpc]" + newline)
        f.write("ip = " + empire_server + newline)
        f.write("port = " + empire_port + newline)
        f.write("username = " + empire_username + newline)
        f.write("password = " + empire_password + newline)
        f.write(newline)
        f.write("[recaptcha]" + newline)
        f.write("site_key = " + recaptcha_site_key + newline)
        f.write("secret_key = " + recaptcha_secret_key + newline)

    # Add first User to database
    db = neo4j.Initialize()

    # TODO (ecolq): Specify correct roles for initial user?
    new_user = {
        "username": ui_username,
        "password": ui_password,
        "job": "Site Administrator",
        "state": "Unknown",
        "country": "Unknown",
        "department": "Unknown",
        "email": "admin@whitelightning",
        "firstname": "Administrator",
        "lastname": "",
        "role_adm": True,
        "role_dev": True,
        "role_eng": True
    }

    create_new_user(new_user, db)

    # Install RAT

    # Random UX configurations

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


def create_new_user(request_form, db):
    profile = user_utils.NewUser(request_form)

    user = db.query_first("MATCH (u:_USER {username: '%s'}) RETURN u" % profile.username)

    if len(user) != 0:
        return "Username already exists"

    query =  "CREATE (u:_USER {username: '" + profile.username + "'}) " 
    query += "SET u.password = '" + profile.encrypted_password + "', " 
    query += "u.firstName = '" + profile.first_name + "', " 
    query += "u.lastName = '" + profile.last_name + "', " 
    query += "u.jobTitle = '" + profile.job_title + "', "
    query += "u.state = '" + profile.state + "', " 
    query += "u.country = '" + profile.country + "', " 
    query += "u.department = '" + profile.department + "', " 
    query += "u.email = '" + profile.email + "', " 
    query += "u.isAdmin = " + profile.is_admin + ", " 
    query += "u.isDev = " + profile.is_dev + ", " 
    query += "u.isEng = " + profile.is_eng + " RETURN u"

    result = db.query_first(query)

    if len(result) == 1:
        return "ok"
    else:
        return "Failed to create user account"


def validate_server(host, port, db=None):
    # TODO(ecolq): Implementation
    return (host, port)


def validate_re_captcha(arg1):
    # TODO(ecolq): Implementation
    return arg1


def validate_re_captcha_keys(arg1, arg2):
    # TODO(ecolq): Implementation
    return True
