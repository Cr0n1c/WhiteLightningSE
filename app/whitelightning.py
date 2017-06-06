import os
import sys
from ConfigParser import SafeConfigParser

from enum import Enum
from flask import Flask
from flask_wtf import CSRFProtect
from werkzeug.utils import redirect

from app.routes import routes, initialise_users_for_routes


class Environment:
    def __init__(self, debug, srvhost, srvport):
        self.DEBUG = debug
        self.SRVHOST = srvhost
        self.SRVPORT = srvport


# Possible Environments to run Flask in
class Environments(Enum):
    DEV = Environment(True, '127.0.0.1', 8080)
    PROD = Environment(False, '0.0.0.0', 80)


if __name__ == '__main__':
    # Default to running in dev mode. This means a) running locally, b) on port 8080 and c) with DEBUG=True
    environment = Environments.PROD if sys.argv[1] and sys.argv[1] == 'prod' else Environments.DEV

    # Reading in config
    parser = SafeConfigParser()

    try:
        with open(os.path.join(os.getcwd(), "..", "conf", "whitelightning.conf")) as f:
            parser.readfp(f)
    except IOError:
        initial_run = True
    else:
        initial_run = False

    csrf = CSRFProtect()

    app = Flask(__name__)
    csrf.init_app(app)

    # Add blueprints
    app.register_blueprint(routes)

    app.config['RECAPTCHA_PUBLIC_KEY'] = parser.get('recaptcha', 'site_key')
    app.config['RECAPTCHA_PRIVATE_KEY'] = parser.get('recaptcha', 'secret_key')
    app.config['RECAPTCHA_DATA_ATTRS'] = {'size': 'compact'}

    while initial_run:
        redirect(to_url('first-run'))

    try:
        initialise_users_for_routes()
        app.secret_key = os.urandom(24)
        app.run(host=environment.SRVHOST, port=environment.SRVPORT, debug=environment.DEBUG)
    except Exception as e:
        print "Error starting Flask server. Check that Neo4J is running."
        sys.exit(1)
