import github3
from .app import app
from .background import redis_client, worker_queue
from .login import User
from .workers import update_user_repos
from flask import json, jsonify, redirect, render_template, request, session, url_for
from flask.ext.login import current_user, login_user
from requests_oauth2 import OAuth2

@app.route('/')
def index():
    """The main view of the site. If the current user has any repos already
    retrieved, we pass it as a context variable to the template and display
    them to the user. Otherwise, the default template (the login screen) is
    presented.
    """
    repos_key = 'repos:{}'.format(current_user.get_id())

    repos = redis_client.get(repos_key)
    if repos:
        repos = json.loads(repos)

    return render_template('index.html', repos=repos)

@app.route('/ajax/repos-ready/')
def repos_ready():
    """An ajax endpoint which will check to see if there are any repos in Redis
    for the currently logged in user. Returns a json-encoded string:

        { "repos_ready": true/false }

    """
    repos_key = 'repos:{}'.format(current_user.get_id())
    return jsonify(repos_ready=repos_key in redis_client)

@app.route('/oauth/login/')
def oauth_login():
    """This is the main entry point for the Github OAuth2 login flow.
    """
    oauth2_handler = _get_oauth2_handler()
    return redirect(oauth2_handler.authorize_url())

@app.route('/oauth/callback/')
def oauth_callback():
    """This is the OAuth2 callback endpoint for Github. If the authorization
    was successful, then we'll have a 'code' parameter in the query string that
    can be exchanged for an access token. This access token can then be used to
    request data from Github on behalf of the authenticated user.
    """
    code = request.args.get('code')

    if code:
        # we got the code, so request the access token from github
        oauth2_handler = _get_oauth2_handler()
        token = oauth2_handler.get_token(code)
        access_token = token['access_token'][0]

        # now that we have the token, get the authenticated user from github
        gh = github3.login(token=access_token)
        gh_user = gh.user()

        # we'll need to store the user as a dict in a few places
        user_info = gh_user.to_json()

        # this is the User object which the login manager will keep track of
        user = User(user_info)

        # store the user details and the access token in redis
        redis_client.set('user:{}'.format(user.get_id()),
                json.dumps(user_info))

        redis_client.set('access_token:{}'.format(user.get_id()), access_token)

        # queue a worker that will pull all repository info
        worker_queue.enqueue(update_user_repos, access_token)

        # log the user in and remember them
        login_user(user, remember=True)

        return redirect(url_for('index'))

    # no code was returned, or it was a bad response, so show an error page
    return render_template('oauth/error.html')

def _get_oauth2_handler():
    """Available via a function call since we need a valid app context to
    execute the "url_for" function in order to determine the redirect uri.
    """
    return OAuth2(client_id=app.config['GITHUB_CLIENT_ID'],
            client_secret=app.config['GITHUB_CLIENT_SECRET'],
            site=app.config['GITHUB_OAUTH_PREFIX'],
            redirect_uri=url_for('oauth_callback', _external=True),
            authorization_url=app.config['GITHUB_AUTHORIZE_PATH'],
            token_url=app.config['GITHUB_ACCESS_TOKEN_PATH'])

