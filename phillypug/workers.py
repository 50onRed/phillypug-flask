import github3
import json
import time
from .background import redis_client

def update_user_repos(access_token):
    # emulate some latency, since github is usually pretty quick to respond
    time.sleep(3)

    # login and get the user and repos
    gh = github3.login(token=access_token)
    user = gh.user()
    repos = [repo.to_json() for repo in gh.iter_repos()]

    # store the repos in redis as a json-encoded string
    repos_key = 'repos:{}'.format(user.id)
    redis_client[repos_key] = json.dumps(repos)
