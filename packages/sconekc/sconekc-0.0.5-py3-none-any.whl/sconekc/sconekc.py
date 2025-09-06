'''
###
# Andre Miguel @ Scontain -- amiguel @ scontain . com
# Set of functions to handle Keycloak access and validation tokens; and JSON and JWT payload
# some work is based on the works from [ixe013] https://gist.github.com/ixe013/f3a7ca48e327a7652554f29be3ee7d46
# DO NOT USE IT IN PRODUCTION DIRECTLY!
# proceed with caution and the best practices of software testing, troubleshooting, change management
'''

import os
import socket
import ssl
import hashlib
import json, requests
from datetime import datetime

import base64
import os.path
import pprint
import sys
import time
import zlib

import cryptography.x509
import cryptography.hazmat.backends
import cryptography.hazmat.primitives
DEFAULT_FINGERPRINT_HASH = cryptography.hazmat.primitives.hashes.SHA256

from flask import request, jsonify, abort
import secrets
import webbrowser as wb
from urllib.parse import urlencode


###
# pad base64url format with '='
# [ixe013]
def pad_base64(data):
    """Makes sure base64 data is padded
    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '='* (4 - missing_padding)
    return data


###
# in case of compressed data
# [ixe013]
def decompress_partial(data):
    """Decompress arbitrary deflated data. Works even if header and footer is missing
    """
    decompressor = zlib.decompressobj()
    return decompressor.decompress(data)


###
# split and decompress JWT. returns 3 objects: JSON header, JSON access token, String signature
# [ixe013]
def decompress(JWT):
    """Split a JWT to its constituent parts. 
    Decodes base64, decompress if required. Returns but does not validate the signature.
    """
    header, jwt, signature = JWT.split('.')

    printable_header = base64.urlsafe_b64decode(pad_base64(header)).decode('utf-8')

    if json.loads(printable_header).get("zip", "").upper() == "DEF":
        printable_jwt = decompress_partial(base64.urlsafe_b64decode(pad_base64(jwt)))
    else:
        printable_jwt = base64.urlsafe_b64decode(pad_base64(jwt)).decode('utf-8')

    # printable_signature = base64.urlsafe_b64decode(pad_base64(signature))

    return json.loads(printable_header), json.loads(printable_jwt), signature

###
# prints a formatted output of the 3 parts of the JWT
# [ixe013]
def showJWT(JWT):
    header, jwt, signature = decompress(JWT)

    print("Header:  ", end="")
    pprint.pprint(header)

    print("Token:   ", end="")
    pprint.pprint(jwt)

    print("Signature:   ", end="")
    pprint.pprint(signature)

    print("Issued at:  {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['iat'])) if 'iat' in jwt else 'Undefined'))
    print("Not before: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['nbf'])) if 'nbf' in jwt else 'Undefined'))
    print("Expiration: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['exp'])) if 'exp' in jwt else 'Undefined'))


###
# returns 6 objects: JSON header, JSON access token, String signature, plus human readable issued, not before, and valid to timestamps
def sliceJWT(JWT):
    header, jwt, signature = decompress(JWT)

    issued="Issued at:  {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['iat'])) if 'iat' in jwt else 'Undefined')
    started="Not before: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['nbf'])) if 'nbf' in jwt else 'Undefined')
    validto="Expiration: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['exp'])) if 'exp' in jwt else 'Undefined')

    return (header, jwt, signature, issued, started, validto)


###
# obtains an access token using grant_type=password. requires the username
def get_access_token(server, realm, client, username, password, cert='cert.pem', key='key.pem'):
    endpoint="protocol/openid-connect/token"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{endpoint}"
        response = sessionkeycloak.post(url,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
            data={"client_id":client, "username":username, "password":password, "grant_type":"password"}, verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        access_token = response.json()['access_token']
        if(access_token == None or access_token == ''):
            return "[ERR]Invalid access token. Body:", response.json()
        return access_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"


###
# retrieves the validation token corresponding to the access token
# returns the same validation token received from Keycloak
def get_validation_token_simple(server, realm, access_token, cert='cert.pem', key='key.pem'):
    endpoint="protocol/openid-connect/userinfo"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{endpoint}"
        response = sessionkeycloak.post(url,
            headers={"Authorization":"Bearer "+access_token},
            verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        s_validation_token = str(response.json()).replace("'", '"').replace(r"True","true").replace(r"False","false")
        b_validation_token = bytes(str(s_validation_token).encode('utf-8'))
        j_validation_token = json.loads(str(b_validation_token.decode('utf-8')))
        return j_validation_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"


###
# retrieves the validation token corresponding to the access token
# returns an enriched validation token received from Keycloak, with clearer identification of the timestamp claims and
# their corresponding human-readable version
def get_validation_token(server, realm, access_token, cert='cert.pem', key='key.pem'):
    endpoint="protocol/openid-connect/userinfo"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{endpoint}"
        response = sessionkeycloak.post(url,
            headers={"Authorization":"Bearer "+access_token},
            verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        s_validation_token = str(response.json()).replace("'", '"').replace(r"True","true").replace(r"False","false")
        b_validation_token = bytes(str(s_validation_token).encode('utf-8'))
        j_validation_token = json.loads(str(b_validation_token.decode('utf-8')))
        # enriching with clearer information from access token
        #j_access_token = json.loads(base64.urlsafe_b64decode(access_token + '=' * (4 - len(access_token) % 4)).decode('utf-8'))
        header, jwt, signature, issued, started, validto = sliceJWT(access_token)
        j_validation_token["accesstokentimestampissuing"] = jwt["iat"]
        j_validation_token["accesstokendatetimeissuing"] = issued
        j_validation_token["accesstokentimestampexpiring"] = jwt["exp"]
        j_validation_token["accesstokendatetimeexpiring"] = validto
        j_validation_token["validationtokentimestampvalidation"] = int(datetime.timestamp(datetime.now()))
        j_validation_token["validationtokendatetimevalidation"] = "Validated on: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(j_validation_token["validationtokentimestampvalidation"])))
        return j_validation_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"


###
# Keycloak user session object to retain information when authenticating through /auth endpoint
class KeycloakSession():
    oauth_state: str
    code_verifier: str
    token: str
    access_token: str
    id_token: str
    touch: bool
    proceed: bool
    def __init__(self):
        self.oauth_state = ""
        self.code_verifier = ""
        self.token = ""
        self.access_token = ""
        self.id_token = ""
        self.touch = False
        self.proceed = False


###
# used to create a business logic to handle the redirect_uri request and to obtain the access token
# can be used as a url handler in Flask routes, for example: @app.route("/callback")
def callback_endpoint(kcsession: KeycloakSession, request: request, server, realm, client, redirect_uri):
    endpoint="protocol/openid-connect/token"

    err = request.args.get("error")
    if err:
        desc = request.args.get("error_description", "")
        return abort(400, f"OAuth error: {err} {desc}")

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return abort(400, "Missing code or state.")

    # Validate CSRF state
    saved_state = kcsession.oauth_state
    if not saved_state or state != saved_state:
        return abort(400, "Invalid state.")

    # Retrieve PKCE verifier
    code_verifier = kcsession.code_verifier
    if not code_verifier:
        return abort(400, "Missing PKCE verifier in session.")

    # Exchange the code for tokens
    token_url = f"{server}/realms/{realm}/{endpoint}"
    data = {
        "grant_type": "authorization_code",
        "client_id": client,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    try:
        resp = requests.post(token_url, data=data, timeout=10, verify=False)
    except requests.RequestException as e:
        kcsession.touch = True
        return abort(502, f"Token request failed: {e}")

    if resp.status_code != 200:
        kcsession.touch = True
        return abort(resp.status_code, f"Token endpoint error: {resp.text}")

    tokens = resp.json()

    if "id_token" not in tokens or "access_token" not in tokens:
        return abort(502, f"Unexpected token response: {tokens}")

    # Store ID token in session for logout
    kcsession.id_token = tokens.get("id_token")

    # Clear one-time values
    kcsession.oauth_state = ""
    kcsession.code_verifier = ""

    kcsession.touch = True
    kcsession.proceed = True
    kcsession.access_token_json = resp.text
    #return jsonify(tokens)
    return "<html><head><title>NEARDATA Keycloak Identity and Access Manager</title></head><body><b>You can close the browser now</b></body></html>"


###
# base64url without padding
def b64url_no_pad(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


###
# make a PKCE code_verifier and its S256 code_challenge
def make_pkce_pair() -> tuple[str, str]:
    # RFC 7636: 43–128 chars from unreserved chars. We’ll use 64 random bytes → b64url
    verifier = b64url_no_pad(os.urandom(64))
    challenge = b64url_no_pad(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


###
# opens a browser window to login using Keycloak web page. Keycloak will redirect the logged in user to the redirect_uri informed
# browser and browser parameters can be passed as well, in case you prefer not to use the system's default browser. example:
# login_browser_auth(kcsession, SERVER, REALM, CLIENT, REDIRECT_URI, '/usr/bin/opera', '--private')
# otherwise, the default browser is called
# it does not lock the execution; program can proceed and attest the state later using the KeycloakSession.touch: bool attribute
def login_browser_auth(kcsession: KeycloakSession, server, realm, client, redirect_uri, browser="", browser_params=""):
#def login_browser_auth():
    endpoint="protocol/openid-connect/auth"

    # CSRF state
    state = secrets.token_urlsafe(24)

    # PKCE
    code_verifier, code_challenge = make_pkce_pair()

    # Persist for the callback
    kcsession.oauth_state = state
    kcsession.code_verifier = code_verifier

    # Build the /auth URL (your original URL, but with dynamic state & PKCE)
    auth_params = {
        "response_type": "code",
        "client_id": client,
        "redirect_uri": redirect_uri,
        "scope": "openid",
        "state": state,
        "ui_locales": "en",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{server}/realms/{realm}/{endpoint}?{urlencode(auth_params)}"

    if browser != "":
        prog = wb.BackgroundBrowser(browser)
        prog.args = {browser_params, '%s'}
        wb.register(browser, None, prog)
        wb.get(browser).open_new(f'{auth_url}')
    else:
        wb.open_new(f'{auth_url}')


###
# ends current session and cleans the session object
def logout_session(kcsession: KeycloakSession, server, realm):
    endpoint="protocol/openid-connect/logout"
    # Retrieve ID token if available (optional)
    id_token = kcsession.id_token

    # Clear local session
    kcsession = None

    # Build logout URL
    logout_url = f"{server}/realms/{realm}/{endpoint}"
    params = {}

    if id_token:
        params["id_token_hint"] = id_token

    sessionkeycloak = requests.Session()
    response = sessionkeycloak.post(logout_url, data=params, verify=False)
    if(response.status_code != 200):
        print("[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json())
    else:
        print("User logged out")
