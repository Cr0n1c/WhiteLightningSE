import datetime
import hashlib
import json
import os
import requests

from ConfigParser import SafeConfigParser
#custom libraries
import neo4j
import userUtils

#template libraries
import templateUserControlPanel
import templateLogin

requests.packages.urllib3.disable_warnings()

def firstRun(request_form):
    try:
        db_server = request_form["dbserver"]
        db_username = request_form["dbusername"]
        db_password = request_form["dbpassword"]
            
        ui_username = request_form["uiusername"]
        ui_password = request_form["uipassword"]

        empire_server = request_form["empireserver"]
        empire_port = request_form["empireport"]
        empire_username = request_form["empireusername"]
        empire_password = request_form["empirepassword"]

        recaptcha_site_key = request_form["recaptchasite"]
        recaptcha_secret_key = request_form["recaptchasecret"]
    except KeyError:    
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}
    
    if validateServer(db_server, None, "neo4j") and validateUser(db_username) and validatePass(db_password) and \
       validateServer(empire_server, empire_port) and validateUser(empire_username) and validatePass(empire_password) \
       and validateUser(ui_username) and validatePass(ui_password) \
       and validateReCaptcha(recaptcha_site_key, recaptcha_secret_key):
        pass
    else: 
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}

    #Build INI file
    newline = "\n"
    with open(os.parth.join(os.getcwd(), "..", "conf", "whitelightning.conf"), "w") as f:
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

    #Build the database
    url = "https://" + db_server.split(":")[1] + ":7473/user/neo4j/password"
    headers = { "content-type" : "application/json",
                "Authorization": "Basic bmVvNGo6bmVvNGo="
              }
    payload = {"password" : db_password}

    r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    if r.status_code != 200:
        return json.dumps({'success': False}), r.status_code, {'ContentType': 'application/json'}
    
    #Add first User to database
    db = kore.neo4j.Initialize()
    
    newUser = { "username" : ui_username,
                "password" : ui_password,
                "job" : "Site Administrator",
                "state" : "Unknown",
                "country" : "Unknown",
                "department": "Unknown",
                "email" : "admin@whitelightning",
                "firstname": "Administator",
                "lastname": "",
                "role_adm": True,
                "role_dev": True,
                "role_eng": True
             }
    
    createNewUser(newUser, db)

    #Install RAT

    #Random UX configurations

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

def createNewUser(request_form, db):
    profile = userUtils.NewUser(request_form)

    user = db.queryFirst("MATCH (u:_USER {username: '%s'}) RETURN u" %profile.username)

    if len(user) != 0:
        return "Username already exists"

    query = "CREATE (u:_USER {username: '"+profile.username+"'}) "\
            "SET u.password = '"+profile.encrypted_password+"', " \
            "u.firstName = '"+profile.first_name+"', "\
            "u.lastName = '"+profile.last_name+"', "\
            "u.jobTitle = '"+profile.job_title+"', "\
            "u.state = '"+profile.state+"', "\
            "u.country = '"+profile.country+"', "\
            "u.department = '"+profile.department+"', "\
            "u.email = '"+profile.email+"', "\
            "u.isAdmin = "+profile.is_admin+", "\
            "u.isDev = "+profile.is_dev+", "\
            "u.isEng = "+profile.is_eng+" RETURN u"

    result = db.queryFirst(query)

    if len(result) == 1:
        return "ok"
    else:
        return "Failed to create user account"

def validateUser(username):
    return True

def validateServer(host, port, db=None):
    return True

def validateReCaptcha(site_str, secret_str):
    return True
