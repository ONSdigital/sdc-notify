import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from jwt import encode, decode
from jose.exceptions import JWTError
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, desc

# service name (initially used for sqlite file name and schema name)
SERVICE_NAME = 'bsdc-notify'
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME', 'dev')

app = Flask(__name__)

# Enable cross-origin requests
CORS(app)

# Set up the database, using configuration if available:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/{}.db'.format(SERVICE_NAME))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
SCHEMA_NAME = None if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite') else '{}_{}'.format(ENVIRONMENT_NAME, SERVICE_NAME)


# Association model
# NB: for delegation we could add start/end dates to associations,
#     which might enable us to fulfil a bunch of user needs (e.g. maternity leave).
class Email(db.Model):
    __table_args__ = {'schema': SCHEMA_NAME}
    # Columns
    id = Column(Integer, primary_key=True)
    to = Column(String(100))
    subject = Column(Text())
    body = Column(Text())
    date = Column(DateTime())

    def __init__(self, to=None, subject=None, body=None):
        self.to = to
        self.subject = subject
        self.body = body
        self.date = datetime.datetime.now()

    def __repr__(self):
        return '<Email to: %r, subject: %r>' % (self.to, self.subject)

    def json(self):
        return {"to": self.to,
                "subject": self.subject,
                "body": self.body}


@app.route('/email', methods=['GET'])
def show_email():
    token = request.headers.get("token")
    if validate_token(token):

        result = {"email": []}

        # Load all associations for this user
        messages = Email.query.order_by(desc(Email.date))
        for message in messages:
            result["email"].append(message.json())

        return jsonify(result)

    return unauthorized("Please provide a valid 'token' header.")


@app.route('/email', methods=['POST'])
def send_email():
    token = request.headers.get('token')
    if not validate_token(token):
        return unauthorized("Please provide a valid 'token' header.")

    data = request.get_json()
    if not data:
        return known_error("Please ensure you're passing application/json.")

    if 'to' in data and 'subject' in data and 'body' in data:
        # Todo: validate email!
        email = Email(data['to'], data['subject'], data['body'])
        db.session.add(email)
        db.session.commit()
        return jsonify(email.json())

    return known_error("Please provide 'to', 'subject' and 'body' in your message.")


@app.errorhandler(401)
def unauthorized(error=None):
    app.logger.error("Unauthorized: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 401

    return resp


@app.errorhandler(400)
def known_error(error=None):
    app.logger.error("Bad request: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp


@app.errorhandler(500)
def unknown_error(error=None):
    app.logger.error("Error: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "Internal server error: " + repr(error),
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


def validate_token(token):

    if token:
        try:
            return decode(token)
        except JWTError:
            return ""
    return ""


def create_database():

    print("Creating tables...")
    db.create_all()
    print("Done")


if __name__ == '__main__':

    # Create database
    print("creating database")
    create_database()

    # Start server
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
