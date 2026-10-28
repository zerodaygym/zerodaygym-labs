# Google DevSite pickle RCE - local lab

Docker lab for my YouTube video. Recreates [Simon Koeck's $90k Google DevSite RCE](https://simonkoeck.com/writeups/google-devsite-flask-session-pickle-rce).
Runs fully local, no real Google/OAuth stuff.

## Run

```bash
docker compose up --build -d
# http://localhost:13337
```

## The bug

Flask session cookie - signed, not encrypted (anyone can decode it)
`/oauth2authorize` - puts a pickled `OAuth2WebServerFlow` in the cookie (with `client_secret`)
`SECRET_KEY` - same value as `client_secret` (so the cookie leaks its own signing key)
`/oauth2callback` - runs `pickle.loads()` on the flow from the session = RCE

## Steps

Get a cookie: `curl -si 'http://localhost:13337/oauth2authorize?return_url=%2F' | grep -i set-cookie`
Decode it, grab `client_secret` (`pickletools.dis()` dumps the pickle)
Build a session with your own pickle (`__reduce__` -> `os.system`) under `google_oauth2_flow_<csrf>`
Sign it with the leaked secret (`flask-unsign` or `cookiemonster`)
Send it to `/oauth2callback` -> shell
Flag is in `/flag.txt`

## Cleanup

```bash
docker compose down --rmi local
```

Bug found by Simon Koeck. This is just a practice recreation.
