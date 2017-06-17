#!/usr/bin/python
from ConfigParser import SafeConfigParser
import json                 
import os                   

from flask import Flask, Blueprint, render_template, redirect, url_for, request, session  
from flask_wtf.csrf import CSRFProtect

import kore
from kore.empirerpc import EmpireRpc


# TODO (ecolq) AWFUL HACK: Remove these globals
global db
global users

def initialise_users_for_routes():
    global db
    global users
    db = kore.neo4j.Initialize()
    users = kore.neo4j.get_all_users()
        
def login_check(**kwargs):
    if not session.get('logged_in'):
        return redirect(url_for('routes.login'))
    else:
        return render_template(
            session.get('current_url'),
            user=users[session.get('username')],
            **kwargs
        )

def update_page(current_title, current_url):
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

#Reading in config
parser = SafeConfigParser()

try:
    with open(os.path.join(os.getcwd(),"..", "conf", "whitelightning.conf")) as f:
        parser.readfp(f)
except IOError:
    initial_run = True
else:
    initial_run = False

csrf = CSRFProtect()

routes = Blueprint('routes', __name__)
app = Flask(__name__)
csrf.init_app(app)

app.config['RECAPTCHA_PUBLIC_KEY'] = parser.get('recaptcha', 'site_key')
app.config['RECAPTCHA_PRIVATE_KEY'] = parser.get('recaptcha', 'secret_key')
app.config['RECAPTCHA_DATA_ATTRS'] = {'size': 'compact'}                           

# Setup EmpireRPC
app.config['EMPIRERPC_IP'] = parser.get('empirerpc', 'ip')
app.config['EMPIRERPC_PORT'] = parser.get('empirerpc', 'port')
app.config['EMPIRERPC_USER'] = parser.get('empirerpc', 'username')
app.config['EMPIRERPC_PASS'] = parser.get('empirerpc', 'password')
empirerpc = EmpireRpc(app.config['EMPIRERPC_IP'],
                      app.config['EMPIRERPC_PORT'],
                      username=app.config['EMPIRERPC_USER'],
                      password=app.config['EMPIRERPC_PASS'])

@routes.route('/')
@routes.route('/home')
@routes.route('/index')
def home():
    update_page("home", "index.html")
    return login_check()

@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = kore.template_login.LoginForm()

    if form.validate_on_submit() and form.username.data in users and \
            kore.neo4j.user_login(form.username.data, form.password.data, db) is None:
        session['username'] = form.username.data
        session['logged_in'] = True
        session['sidebar_collapse'] = False
        return redirect(url_for('routes.home'))
    else:
        return render_template('login.html', form=form)

@routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))

@routes.route('/first-run', methods=['GET', 'POST'])
def first_run():
    if request.method == 'POST':
        status = kore.first_run(request.form)
        if status[1] == 200:
            return login()
    else:
        return render_template('first-run.html')

@routes.route('/user-control-panel', methods=['GET', 'POST'])
def user_control_panel():
    update_page('user_control_panel', 'user-control-panel.html')

    # registration piece
    if request.method == 'POST' and session.get('logged_in'):
        status = kore.create_new_user(request.form, db)
        if status == "ok":
            return redirect(url_for('routes.' + session['current_title']))

    try:
        if not users[session['username']]['is_admin']:
            return redirect(url_for('routes.error'))
    except KeyError:
        return login_check()

    return login_check(ucp=kore.template_user_control_panel.UserControlPanelPage(db))

@routes.route('/update-user-role', methods=['POST'])
def update_user_role():
    status = True
    if session['logged_in'] and users[session['username']]['is_admin']:
        status = kore.template_user_control_panel.update_user_role(
            db,
            request.form['name'],
            request.form['property'],
            request.form['value']
        )

    if status:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}

@routes.route('/user-profile')
def user_profile():
    update_page("userProfile", "user-profile.html")
    return login_check()

@routes.route('/asset-tracking')
def asset_tracking():
    update_page("assetTracking", "asset-tracking.html")
    return login_check()

@routes.route('/asset-discovery')
def asset_discovery():
    update_page("assetDiscovery", "asset-discovery.html")
    return login_check()

@app.route('/terminal', methods=['GET', 'POST'])
def handle_terminal():
    if request.method == 'POST' and session.get('logged_in') and request.args.get('id') is not None:
        command = request.get_json(force=True, silent=True)
        agent_name = request.args.get('id')
        if empirerpc is None:
            success = False
            message = 'Unable to connect to Empire!'
            status_code = 503
        else:
            retval = empirerpc.handle_command(command.get('command', 'help'), agent_name=agent_name)
            success = retval.get('success', False)
            message = retval.get('message', 'Success!' if success else 'Unknown Error!')
            status_code = 200
        return json.dumps({'success':success, 'message':message}), status_code, {'ContentType':'application/json'}

    update_page('terminal','terminal.html')
    return login_check()

###############[ ERROR HANDLING ]########################
@routes.route('/error')
def error():
    pass
