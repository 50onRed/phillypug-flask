from .app import app
from .views import *
from flask.ext.bootstrap import Bootstrap

# Initialize the twitter bootstrap templates for use later
Bootstrap(app)
