import json
import os
from uuid import uuid4
from flask import Flask, request, abort, Response
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from srcs.helpers import send_alerts
from threading import Lock
import time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

env_data = json.load(open('srcs/env.json', 'r'))

cooldown = env_data["data"]["general"]["cooldown"]
server = env_data["data"]["general"]["server"]

async_mode = None

app = Flask(__name__)
socket_ = SocketIO(app, async_mode=async_mode)

# database
file_path = os.path.abspath(os.getcwd()) + r"\data.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
db = SQLAlchemy(app)

thread = None
thread_lock = Lock()


@app.route('/')
def index():
    return 'Success'


if env_data["development"]:
    @app.route('/api/test')
    def test():
        socket_.emit('test_event')
        socket_.emit('raid', server)
        return Response('200')


@app.route('/api/alarm', methods=["POST"])
def rust():
    if request.headers.get('x-auth-key') != env_data["data"]["general"]["auth_key"]:
        abort(403)
    else:
        data = request.json
        alarm_id = data["body"].replace(' ', '').split("id:")[1]
        try:
            alarm_id = int(alarm_id)
        except ValueError:
            return Response(status=400)

        db.session.add(AlarmLog(alarm_id))
        db.session.commit()

        alarm = Alarm.query.filter_by(id=alarm_id).first()

        if alarm.cooldown_expiration > time.time():
            return 'Success [Cooldown]'

        if alarm.send_notification:  # Courtyard, Roof, SAM, Open Core [Ignore Doorcamp]
            user_body = data["body"].replace(f'id:{alarm_id}', '')

            send_alerts(db.session.query(Phone.phone).all(), body=user_body)

            socket_.emit('raid', server)

            alarm.cooldown_expiration = int(time.time()) + cooldown
            db.session.commit()

        return 'Success'


class Phone(db.Model):
    __tablename__ = "phones"

    id = db.Column(db.String, primary_key=True)
    phone = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)

    def __init__(self, phone, user):
        self.id = str(uuid4())
        self.phone = phone
        self.user = user

    def __repr__(self):
        return '<PHONE - {}>'.format(self.phone)


class AlarmLog(db.Model):
    __tablename__ = "alarm_log"
    id = db.Column(db.String, primary_key=True)
    alarm_id = db.Column(db.String, ForeignKey('alarm.id'), nullable=False)
    time = db.Column(db.String, nullable=False)

    def __init__(self, alarm_id):
        self.id = str(uuid4())
        if Alarm.query.filter_by(id=alarm_id).first() is None:
            db.session.add(Alarm(alarm_id))
        self.alarm_id = alarm_id
        self.time = time.time()

    def __repr__(self):
        return '<AlarmLog - {}>'.format(self.id)


class Alarm(db.Model):
    __tablename__ = "alarm"
    id = db.Column(db.Integer, primary_key=True)  # use Rust alarm ID (not UUID)

    send_notification = db.Column(db.Boolean, nullable=False)
    cooldown_expiration = db.Column(db.Integer, nullable=False)
    history = relationship(AlarmLog)

    def __init__(self, alarm_id):
        self.id = alarm_id
        if alarm_id >= 0:
            self.send_notification = True
        else:
            self.send_notification = False

        self.cooldown_expiration = 0

    def __repr__(self):
        return '<Alarm - {}>'.format(self.id)


if __name__ == "__main__":
    socket_.run(app, debug=True, port=6262)