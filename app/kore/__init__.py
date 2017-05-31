import datetime
import hashlib

import neo4j
import templateUserControlPanel
import userUtils

def createNewUser(request_form, db):
    profile = userUtils.NewUser(request_form)

    user = db.queryFirst("MATCH (u:_USER {username: '%s'}) RETURN u" %profile.username)

    if len(user) != 0:
        return "Username already exists"

    query = "CREATE (u:_USER {username: '"+profile.username+"'}) SET u.password = '"+profile.encrypted_password+"', " \
            "u.firstName = '"+profile.first_name+"', u.lastName = '"+profile.last_name+"', u.jobTitle = '"+profile.job_title+"', " \
            "u.state = '"+profile.state+"', u.country = '"+profile.country+"', u.department = '"+profile.department+"', " \
            "u.email = '"+profile.email+"', u.isAdmin = "+profile.is_admin+", u.isDev = "+profile.is_dev+", u.isEng = " \
            +profile.is_eng+" RETURN u"

    result = db.queryFirst(query)

    if len(result) == 1:
        print "Yea!! created a new user"
        return "ok"
    else:
        print "boo, did not create"
        return "Failed to create user account"