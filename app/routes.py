#!/usr/bin/python           
import json                 
import os                   
import kore                 
                            
from ConfigParser import SafeConfigParser
from flask import Flask, render_template, redirect, url_for, request, session  
from flask_wtf import RecaptchaField, FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
from flask_wtf.csrf import CSRFProtect

#########[ GLOBAL PARAMS ]#################                        
DEBUG = True                
SRVHOST = '0.0.0.0'         
SRVPORT = 80                
                            
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

#Reading in config
parser = SafeConfigParser()
with open('../conf/whitelightning.conf') as f:
    parser.readfp(f)

#csrf = CSRFProtect()
      
app = Flask(__name__)
#csrf.init_app(app)
       
app.config['RECAPTCHA_PUBLIC_KEY'] = parser.get('recaptcha', 'site_key')
app.config['RECAPTCHA_PRIVATE_KEY'] = parser.get('recaptcha', 'secret_key')
app.config['RECAPTCHA_DATA_ATTRS'] = {'size': 'compact'}                           
########[ WEB PAGES ]#####################                         

@app.route('/')             
@app.route('/home')         
@app.route('/index')        
def home():                        
    updatePage("home", "index.html")                                
    return loginCheck()

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired('A username is required!'), Length(min=7, max=15, message='Invalid Username')], render_kw={"placeholder": "Username"})
    password = PasswordField('password', validators=[InputRequired('Password is required!')], render_kw={"placeholder": "Password"})
    recaptcha = RecaptchaField()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit() and users[form.username.data] and kore.neo4j.userLogin(form.username.data, form.password.data, db) is None:
        session['username'] = form.username.data
        session['logged_in'] = True
        session['sidebar_collapse'] = False
        return redirect(url_for('home'))
    else:
        return render_template('login.html', form=form)

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

###############[ ERROR HANDLING ]########################
@app.route('/error')
def error():
    pass

if __name__ == '__main__':
    users = kore.neo4j.getAllUsers()
    db = kore.neo4j.Initialize()
    app.secret_key = os.urandom(24)
    app.run(host=SRVHOST, port=SRVPORT, debug=DEBUG)
