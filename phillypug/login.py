import github3
import json
from flask.ext.login import LoginManager, UserMixin
from github3 import GitHubError
from github3.users import User as GithubUser
from .background import redis_client

# the main login manager instance
login_manager = LoginManager()
login_manager.login_view = 'oauth_login'

class User(UserMixin):
    """Represents a User in our system. The info attribute will contain a dict
    of the user's details that were obtained from the Github login.
    """
    def __init__(self, info):
        self.info = info

    def get_id(self):
        """The id is how we uniquely identify the user.
        """
        return self.info['id']

@login_manager.user_loader
def load_user(id):
    """Any time the login manager needs to load the User object, we simply pull
    the info out of Redis and return a User object with these details.

    Returning None will mean that the user cannot be retrieved and is therefore
    still anonymous.
    """
    user_info = redis_client.get('user:{}'.format(id))
    if user_info:
        # we're storing the user info as a json-encoded string, so decode first
        return User(json.loads(user_info))
