import userUtils

class UserControlPanelPage(object):

    def __init__(self, db):
        self.db = db

    def __del__(self):
        self.db = None

    def queryAllUser(self):
        user_list = []
        query_string = "MATCH (u:_USER) return u.firstName, u.lastName, u.username, "\
                       "u.email, u.country, u.isEng, u.isDev, u.isAdmin"

        unique_id = 0
        for res in self.db.queryAll(query_string):
            unique_id += 1
            user = userUtils.UserInformation()
            user.first_name = userUtils.setName(res['u.firstName'])
            user.last_name = userUtils.setName(res['u.lastName'])
            user.username = userUtils.setUsername(res['u.username'])
            user.email = userUtils.setEmail(res['u.email'])
            user.country = userUtils.setCountry(res['u.country'])
            user.full_name = userUtils.setFullName(user.first_name, user.last_name)
            user.id = unique_id

            user.is_eng = res['u.isEng']
            user.is_dev = res['u.isDev']
            user.is_admin = res['u.isAdmin']

            for k in [user.is_admin, user.is_eng, user.is_dev]:
                if k == "true":
                    k = True
                else:
                    k = False
            user_list.append(user)

        return user_list

    def flipStatus(self, current_status):
        if current_status == "true":
            new_status = "false"
        elif current_status == "false":
            new_status = "true"
        else:
            new_status = None

        return new_status

    def toggleStatus(self, username, field_to_update, current_status):
        new_status = flipStatus(current_status)

        if new_staus is None or not setUsername(username) or \
          field_to_update not in ['isAdmin', 'isEng', 'isDev']:
            return False

        self.db.query("MERGE (u:_USER {username: '%s'}) set u.%s = %s" %
            (username, field_to_update, current_status))

def updateUserRole(db, user, prop, value):
    prop_dic = { 'admin' : 'isAdmin',
                  'dev'   : 'isDev',
                  'eng'   : 'isEng'
                }

    if not prop in prop_dic.keys() or not value in ['true', 'false']:
        return False

    db.queryAll("MATCH (u:_USER {username: '%s'}) set u.%s = %s" %
        (user, prop_dic[prop], value))
    return True
