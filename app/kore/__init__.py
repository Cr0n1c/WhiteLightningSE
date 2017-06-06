import json
import os

import urllib3

import neo4j
import template_login
import template_user_control_panel
import user_utils

urllib3.disable_warnings()


def first_run(request_form):
    try:
        db_server, none = validate_server(request_form["dbserver"], None, "neo4j")
        db_username = user_utils.set_username(request_form["dbusername"])
        db_password = request_form["dbpassword"]

        ui_username = user_utils.set_username(request_form["uiusername"])
        ui_password = user_utils.set_password(ui_username, request_form["uipassword"])

        (empire_server, empire_port) = validate_server(request_form["empireserver"], request_form["empireport"])
        empire_username = user_utils.set_username(request_form["empireusername"])
        empire_password = user_utils.set_password(None, request_form["empirepassword"], False)

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
    with open(os.path.join(os.getcwd(), "..", "conf", "whitelightning.conf"), "w") as f:
        f.write("[server]" + newline)
        f.write("ip = 0.0.0.0" + newline)
        f.write("port = 80" + newline)
        f.write(newline)
        f.write("[database]" + newline)
        f.write("url = " + db_server + newline)
        f.write("username = " + db_username + newline)
        f.write("password = " + db_password + newline)
        f.write(newline)
        f.write("[empire]" + newline)
        f.write("server = " + empire_server + newline)
        f.write("port = " + empire_port + newline)
        f.write("username = " + empire_username + newline)
        f.write("password = " + empire_password + newline)
        f.write(newline)
        f.write("[recaptcha]" + newline)
        f.write("site_key = " + recaptcha_site_key + newline)
        f.write("secret_key = " + recaptcha_secret_key + newline)

    # Build the database
    # url = "https:" + db_server.split(":")[1] + ":7473/user/neo4j/password"
    # base64_username_password = base64.b64encode("{}:{}".format(db_username, db_password))
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "Basic " + base64_username_password
    #     }
    # payload = {"password": db_password}
    #
    # r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    # if r.status_code != 200:
    #     return json.dumps({'success': False}), r.status_code, {'ContentType': 'application/json'}

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
        "firstname": "Administator",
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

    query = "CREATE (u:_USER {username: '" + profile.username + "'}) " \
            "SET u.password = '" + profile.encrypted_password + "', " \
            "u.firstName = '" + profile.first_name + "', " \
            "u.lastName = '" + profile.last_name + "', " \
            "u.jobTitle = '" + profile.job_title + "', " \
            "u.state = '" + profile.state + "', " \
            "u.country = '" + profile.country + "', " \
            "u.department = '" + profile.department + "', " \
            "u.email = '" + profile.email + "', " \
            "u.isAdmin = " + profile.is_admin + ", " \
            "u.isDev = " + profile.is_dev + ", " \
            "u.isEng = " + profile.is_eng + " RETURN u"

    result = db.query_first(query)

    if len(result) == 1:
        return "ok"
    else:
        return "Failed to create user account"


def validate_server(host, port, db=None):
    # TODO(ecolq): Implementation
    return (host, port)
    # if port:
    #     if re.match("^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$", port):
    #         return True, True
    #     else:
    #         return True, False
    # else:


def validate_re_captcha(arg1):
    # TODO(ecolq): Implementation
    return arg1


def validate_re_captcha_keys(arg1, arg2):
    return True
