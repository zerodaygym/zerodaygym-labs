import json
import os
import secrets
from urllib.parse import urlencode

from flask import Flask, abort, jsonify, render_template, request, session
from jinja2 import TemplateNotFound
from oauth2client.contrib.flask_util import UserOAuth2

app = Flask(__name__)

# One OAuth client is shared by every docs deployment.
CLIENT_ID = os.environ.get(
    'OAUTH_CLIENT_ID', '480529417306-n4b2k8q0m7h3.apps.nimbusauth.dev')
CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET') or 'GOCSPX-' + secrets.token_urlsafe(21)

app.config.update(
    SECRET_KEY=CLIENT_SECRET,
    GOOGLE_OAUTH2_CLIENT_ID=CLIENT_ID,
    GOOGLE_OAUTH2_CLIENT_SECRET=CLIENT_SECRET,
)

oauth2 = UserOAuth2(
    app,
    auth_uri='/signin/oauth/v2/auth',
    token_uri='http://127.0.0.1:8080/oauth2/v4/token',
)


@app.before_request
def keep_signin_session():
    if request.endpoint == 'oauth2.authorize':
        session.permanent = True


@app.route('/', defaults={'slug': 'index'})
@app.route('/docs/<slug>')
def docs(slug):
    try:
        return render_template(f'docs/{slug}.html', slug=slug)
    except TemplateNotFound:
        abort(404)


# --- Stand-ins for the identity provider (accounts / oauth2 token endpoint) ---

@app.route('/signin/oauth/v2/auth')
def signin():
    a = request.args
    back = a.get('redirect_uri', '/oauth2callback')
    allow = back + '?' + urlencode({
        'state': a.get('state', ''),
        'code': '4/0A' + secrets.token_urlsafe(40),
        'scope': a.get('scope', ''),
    })
    deny = back + '?' + urlencode({'error': 'access_denied'})
    return render_template('signin.html', client_id=a.get('client_id', ''), allow=allow, deny=deny)


@app.post('/oauth2/v4/token')
def token():
    import base64 as _b64
    def _seg(obj):
        return _b64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b'=').decode()
    header = _seg({"alg": "RS256", "typ": "JWT"})
    payload = _seg({
        "iss": "accounts.nimbus.dev",
        "sub": "100000000000000000001",
        "email": "demo@nimbus.example",
        "email_verified": True,
        "aud": CLIENT_ID,
        "iat": int(__import__('time').time()),
        "exp": int(__import__('time').time()) + 3600,
    })
    fake_sig = secrets.token_urlsafe(43)
    return jsonify(
        access_token='ya29.lab-' + secrets.token_urlsafe(30),
        token_type='Bearer',
        expires_in=3600,
        id_token=f'{header}.{payload}.{fake_sig}',
    )


@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404
