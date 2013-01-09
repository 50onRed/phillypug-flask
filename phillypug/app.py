from flask import Flask

# creates the main Flask application and configures it
app = Flask(__name__)
app.config.from_pyfile('config.py')

# sets up the login manager, which will handle our user logins
from .login import login_manager
login_manager.setup_app(app)
