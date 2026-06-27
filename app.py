from flask import Flask, redirect, session, url_for, request, flash
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
)

oauth = OAuth(app)
twitter = oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/2/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    client_id=os.environ.get('TWITTER_CONSUMER_KEY'),
    client_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
)


@app.route('/login')
def login():
    redirect_uri = url_for('oauth_authorized', _external=True)
    return twitter.authorize_redirect(redirect_uri)


@app.route('/oauth-authorized')
def oauth_authorized():
    next_url = request.args.get('next') or url_for('hello_world')
    token = twitter.authorize_access_token()
    if token is None:
        flash('You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = token
    resp = twitter.get('users/me')
    user_info = resp.json()
    session['twitter_user'] = user_info.get('data', {}).get('username', 'unknown')

    flash('You were signed in as %s' % session['twitter_user'])
    return redirect(next_url)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
