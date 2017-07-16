import time
    irint profile.is_eng

###########[ HELPER FUNCTIONS ]################
def validate_mandatory_keys(dic, mandatory_key_list):
    for key in mandatory_key_list:
        if key not in dic:
            return False

    return True

def build_query_from_dic(dic, neo_var="c", add_timestamp=True):
    query_str = ""
    var = neo_var + "."
    
    if add_timestamp:
        query_str += var + "timestamp=" + str(time.time()) + "," 

    for k, v in dic.items():
        key = k + "="
        value = "'" + v + "',"
        query_str += var + key + value

    #Chopping off the final , before returning
    return query_str[:-1] 


##########[ QUERY FUNCTIONS ]#################
def survey_result(result_dic, db):
    mandatory_keys = ["campaign"]
    if not validate_mandatory_keys(result_dic, mandatory_keys):
        return

    query_str = build_query_from_dic(result_dic)
    db.query_first("CREATE (c:Campaign {type: 'survey_result'}) SET " + query_str)

def credential_thief_result(result_dic, db):
    mandatory_keys = ["username", "password", "redirect_url", "campaign"]
    if not validate_mandatory_keys(result_dic, mandatory_keys):
        return
    
    query_str = build_query_from_dic(result_dic)
    db.query_first("CREATE (c:Campaign {type: 'credential_thief'}) SET " + query_str)

