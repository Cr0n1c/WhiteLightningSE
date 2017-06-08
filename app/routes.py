#!/usr/bin/python           
import json
import kore

from flask import Blueprint
from flask import render_template, redirect, url_for, request, session

routes = Blueprint('routes', __name__)

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


###############[ ERROR HANDLING ]########################
@routes.route('/error')
def error():
    pass
