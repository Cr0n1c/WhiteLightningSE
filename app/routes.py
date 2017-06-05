#!/usr/bin/python           
import json                 
import os                   
import kore
from kore.empirerpc import EmpireRpc
                           
from flask import Flask, render_template, redirect, url_for, request, session  
                       
#########[ GLOBAL PARAMS ]#################                        
DEBUG = True                
SRVHOST = '0.0.0.0'
SRVPORT = 8001
         
#########[ BASIC MODULES ]#################                        
def loginCheck(**kwargs):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template(session.get('current_url'), user=users[session.get('username')], **kwargs)

def updatePage(current_title, current_url):
    if current_url == session.get('current_url'):
        return

    if session.get('previous_url') is None:
        session['previous_url'] = "index.html"
        session['previous_title'] = "home"

    session['previous_url'] = session.get('current_url')
    session['previous_title'] = session.get('current_title')
    session['current_url'] = current_url
    session['current_title'] = current_title
                       
#########[ APP STARTUP ]###################                        
app = Flask(__name__)       

# Setup EmpireRPC
empirerpc = EmpireRpc('104.236.48.159',23698,username='empirerpc',password='test123test!@#')
                            
########[ WEB PAGES ]#####################                         
@app.route('/')             
@app.route('/home')         
@app.route('/index')        
def home():                        
    updatePage("home", "index.html")                                
    return loginCheck()

@app.route('/login', methods=['GET', 'POST'])
def login():
    global users
    error = { 'code'   : None,
              'message': None
            }

    if request.method == 'POST':
        try:
            username = request.form['username'].lower()
            password = request.form['password']
        except KeyError:
            error['code'] = 2 #User is bypassing the UX
            error['message'] = "Malicious login attempt"
        else:
            if users.get(username) is None:
                error['code'] = 3 #User does not exists
                error['message'] = "Invalid Creds"
            else:
                error['message'] = kore.neo4j.userLogin(username, password, db)
                if error['message'] and users[username]:
                    try:
                        users[username]['login_atttempt'] += 1
                    except KeyError:
                        users[username]['login_attempt'] = 1
                        error['code'] = 4 #Failed login
                    else:
                        if users[username]['login_attempt'] > 2:
                             error['code'] = 5 #Force reCaptcha
                        else:
                             error['code'] = 4 #Failed login

        if error['code'] is None:
            session['username'] = username
            session['logged_in'] = True
            session['login_attempt'] = 0
            session['sidebar_collapse'] = False
            return redirect(url_for('home'))
        else:
            print error
            return render_template('login.html', error=error)
    elif request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user-control-panel', methods=['GET', 'POST'])
def userControlPanel():
    updatePage('userControlPanel', 'user-control-panel.html')

    #registration piece
    if request.method == 'POST' and session.get('logged_in'):
        status = kore.createNewUser(request.form, db)
        if status == "ok":
            return redirect(url_for(session['current_title']))

    try:
        if not users[session['username']]['is_admin']:
            return redirect(url_for('error'))
    except KeyError:
        return loginCheck()

    return loginCheck(ucp = kore.templateUserControlPanel.UserControlPanelPage(db))

@app.route('/update-user-role', methods=['POST'])
def updateUserRole():
    status = True
    if session['logged_in'] and users[session['username']]['is_admin']:
        status = kore.templateUserControlPanel.updateUserRole(db, request.form['name'], request.form['property'], request.form['value'])
    else:
        print "something is going horrible"

    if status:
        print "status is good"
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    else:
        print "statis is no good"
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'}

@app.route('/user-profile')
def userProfile():
    updatePage("userProfile", "user-profile.html")
    return loginCheck()

@app.route('/asset-tracking')
def assetTracking():
    updatePage("assetTracking", "asset-tracking.html")
    return loginCheck()

@app.route('/asset-discovery')
def assetDiscovery():
    updatePage("assetDiscovery", "asset-discovery.html")
    return loginCheck()

@app.route('/terminal',methods=['GET','POST'])
def handleTerminal():
    if request.method == 'POST' and session.get('logged_in') and request.args.get('id') is not None:
        command = request.get_json(force=True,silent=True)
        agent_name = request.args.get('id')
        if empirerpc is None:
            success = False
            message = 'Unable to connect to Empire!'
            status_code = 503
        else:
            retval = empirerpc.handle_command(command.get('command','help'),agent_name=agent_name)
            success = retval.get('success',False)
            message = retval.get('message',"Success!" if success else "Unknown Error!")
            status_code = 200
        return json.dumps({'success':success,'message':message}), status_code, {'ContentType':'application/json'}

    updatePage("terminal", "terminal.html")
    return loginCheck()

###############[ ERROR HANDLING ]########################
@app.route('/error')
def error():
    pass

if __name__ == '__main__':
    users = kore.neo4j.getAllUsers()
    db = kore.neo4j.Initialize()
    app.secret_key = os.urandom(24)
    app.run(host=SRVHOST, port=SRVPORT, debug=DEBUG)
