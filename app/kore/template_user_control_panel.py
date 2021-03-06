import user_utils


class UserControlPanelPage(object):
    def __init__(self, db):
        self.db = db

    def __del__(self):
        self.db = None

    def query_all_user(self):
        user_list = []
        query_string = "MATCH (u:_USER) return u.firstName, u.lastName, u.username, " \
                       "u.email, u.country, u.isEng, u.isDev, u.isAdmin"

        unique_id = 0
        for res in self.db.query_all(query_string):
            unique_id += 1
            user = user_utils.UserInformation()
            user.first_name = user_utils.set_name(res['u.firstName'])
            user.last_name = user_utils.set_name(res['u.lastName'])
            user.username = user_utils.set_username(res['u.username'])
            user.email = user_utils.set_email(res['u.email'])
            user.country = user_utils.set_country(res['u.country'])
            user.full_name = user_utils.set_full_name(user.first_name, user.last_name)
            user.id = unique_id

            user.is_eng = res['u.isEng']
            user.is_dev = res['u.isDev']
            user.is_admin = res['u.isAdmin']

            # TODO (ecolq): Figure out what this is used for/remove?
            user_list.append(user)

        return user_list

    def flip_status(self, current_status):
        if current_status == "true":
            new_status = "false"
        elif current_status == "false":
            new_status = "true"
        else:
            new_status = None

        return new_status

    def toggle_status(self, username, field_to_update, current_status):
        new_status = self.flip_status(current_status)

        if new_status is None or not user_utils.set_username(username) or \
                field_to_update not in ['isAdmin', 'isEng', 'isDev']:
            return False

        self.db.query("MERGE (u:_USER {username: '%s'}) set u.%s = %s" %
                      (username, field_to_update, current_status))


def update_user_role(db, user, prop, value):
    prop_dic = {
        'admin': 'isAdmin',
        'dev': 'isDev',
        'eng': 'isEng'
    }

    if not prop in prop_dic.keys() or not value in ['true', 'false']:
        return False

    db.query_all("MATCH (u:_USER {username: '%s'}) set u.%s = %s" %
                 (user, prop_dic[prop], value))
    return True
