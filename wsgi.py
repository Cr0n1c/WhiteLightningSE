from app.routes import app, SRVHOST, SRVPORT, DEBUG
import os

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host=SRVHOST, port=SRVPORT, debug=DEBUG)
