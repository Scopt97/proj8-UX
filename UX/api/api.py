# Credit: https://blog.miguelgrinberg.com/post/restful-authentication-with-flask for parts of the authentication implementation
#TODO merge app.py (brevet calculator) with api ?
#TODO jsonify results from resources ?


import flask
from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import os
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)
import time
from flask_httpauth import HTTPBasicAuth
# Instantiate the app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'Secure Phra_se'
auth = HTTPBasicAuth()

client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.tododb
#userdb = client.userdb #TODO delete if below works
users = db.userdb  # The users collection
current_id = 0  # The unique id that will be given to the next user


class All(Resource):
    def get(self):
        token = request.headers.get('token')  # Get the token from a 'token' header, then verify it
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)  # top+1 because just 'top' returned 1 value too few when sorting

        else:
            data = db.tododb.find()

        data.sort('name')
        open_close = {}

        for pair in data:
            name = pair['name']
            desc = pair['description']
            open_close[name] = desc
            
        return open_close

class Open(Resource):
    def get(self):
        token = request.headers.get('token')
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)

        else:
            data = db.tododb.find()

        data.sort('name')
        opens = {}

        for pair in data:
            name = pair['name']
            desc = pair['description']
            open_time = desc[0]
            opens[name] = open_time

        return opens

class Close(Resource):
    def get(self):
        token = request.headers.get('token')
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)

        else:
            data = db.tododb.find()

        data.sort('name')
        closures = {}

        for pair in data:
            name = pair['name']
            desc = pair['description']
            close_time = desc[1]
            closures[name] = close_time

        return closures

class AllCSV(Resource):
    def get(self):
        token = request.headers.get('token')
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)

        else:
            data = db.tododb.find()

        data.sort('name')
        csv = "km, open, close\n"  # column header

        for pair in data:
            name = pair['name']
            desc = pair['description']
            open_time = desc[0]
            close_time = desc[1]
            csv += name + ', ' + open_time + ',' + close_time + '\n'

        return csv

class OpenCSV(Resource):
    def get(self):
        token = request.headers.get('token')
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)

        else:
            data = db.tododb.find()

        data.sort('name')
        opens = "km, open\n"  # column header

        for pair in data:
            name = pair['name']
            desc = pair['description']
            open_time = desc[0]
            opens += name + ', ' + open_time + '\n'

        return opens

class CloseCSV(Resource):
    def get(self):
        token = request.headers.get('token')
        authorized = verify_auth_token(token)

        if not authorized:
            return "token expired or invalid", 401

        if request.args.get('top'):  # if 'top' parameter was given
            top = request.args.get('top')
            top = int(top)
            data = []
            data = db.tododb.find().limit(top+1)

        else:
            data = db.tododb.find()

        data.sort('name')
        closures = "km, close\n"  # column header

        for pair in data:
            name = pair['name']
            desc = pair['description']
            close_time = desc[1]
            closures += name + ', ' + close_time + '\n'

        return closures


def hash_password(password):
    return pwd_context.encrypt(password)

@auth.verify_password
def verify_password(username, password):
    db_entry_cursor = users.find({"username": username})
    if not db_entry_cursor.count():  # If the user is not in the database, return unauthorized
        return False

    db_entry = db_entry_cursor[0]

    pass_hash = db_entry["password"]

    if pwd_context.verify(password, pass_hash):
        return db_entry  # to get user id for token
    else:
        return False


def generate_auth_token(user_id, expiration=30):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    # pass index of user
    token = s.dumps({'id': user_id})
    return {'token': token, 'duration': expiration}

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])

    if not token:  # If no token was given
        return None

    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"


@app.route("/api/register/page")
def register_page():
    return flask.render_template("register.html")


@app.route("/api/register", methods=['POST'])
def register():
    global current_id
    taken_names = users.distinct("username")  # Get taken usernames from the database

    username = request.form.get("username")
    password = request.form.get("password")
    if (username == None) or (password == None):
        return 'Username and password must be provided', 400
    if (username in taken_names) or (':' in username) or (':' in password):  # If the username is taken, username or password is blank, or either contains a ':' (seperator for http basic auth) return bad request
        return "Bad username (taken or contains ':')", 400

    pass_hash = hash_password(password)
    password = None  # Discard password

    new_user = {"_id": current_id, "username": username, "password": pass_hash}
    users.insert_one(new_user)

    response = {"Location": current_id, "username": username, "password": pass_hash}

    current_id += 1

    return flask.jsonify(result=response), 201


@app.route("/api/token/page")
def token_page():
    return flask.render_template("token.html")

@app.route("/api/token", methods=['GET'])
@auth.login_required
def get_token():
    username = request.authorization.username  # get the username, then the db entry for the user
    db_entry_cursor = users.find({"username": username})
    db_entry = db_entry_cursor[0]

    user_id = db_entry["_id"]
    token_duration_pair = generate_auth_token(user_id)
    token = token_duration_pair['token']
    duration = token_duration_pair['duration']

    token_str = str(token)[2:-1]  # Need to chop off b' and beginning and ' at end
    response = {'token': token_str, 'duration': duration}
    return flask.jsonify(result=response)


# Create routes
# Another way, without decorators
api.add_resource(All, '/', '/listAll', '/listAll/json', '/listAll/', '/listAll/json/')  # Adding option for '/' at the end in case the browser automatically adds it

api.add_resource(Open, '/listOpenOnly', '/listOpenOnly/json', '/listOpenOnly?<int:top>', '/listOpenOnly/json?<int:top>', '/listOpenOnly/', '/listOpenOnly/json/')

api.add_resource(Close, '/listCloseOnly', '/listCloseOnly/json', '/listCloseOnly/', '/listCloseOnly/json/')

api.add_resource(AllCSV, '/listAll/csv', '/listAll/csv/')
api.add_resource(OpenCSV, '/listOpenOnly/csv', '/listOpenOnly/csv/')
api.add_resource(CloseCSV, '/listCloseOnly/csv', '/listCloseOnly/csv/')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
