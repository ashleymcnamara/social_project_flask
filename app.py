from flask import Flask
from flask_oauth import OAuth
from flask import redirect, session, url_for, request, flash
import os 

app = Flask(__name__)

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key= os.environ.get('TWITTER_CONSUMER_KEY'),
    consumer_secret= os.environ.get('TWITTER_CONSUMER_SECRET'),
)

app.config.update(
    DEBUG=True,
    SECRET_KEY= os.environ.get('SECRET_KEY'),
)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('hello_world')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)

@app.route('/')
def hello_world():
    return 'Hello World!'

# @app.route('/list/')
# def list():
# 	return 'test'

if __name__ == '__main__':
    app.run()