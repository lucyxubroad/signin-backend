from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os

db = SQLAlchemy()

event_user_table = db.Table('event_user_association',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    club = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=False)
    event_creator = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attendees = db.relationship('User', cascade='delete', secondary=event_user_table)

    def __init__(self, **kwargs):
        self.event = kwargs.get('event', '')
        self.club = kwargs.get('club', '')
        self.location = kwargs.get('location', '')
        self.description = kwargs.get('description', '')
        self.event_creator = kwargs.get('event_creator')
        self.photo = kwargs.get('photo', '')
        
    def serialize(self):
        return {
            'id': self.id,
            'event': self.event,
            'club': self.club,
            'location': self.location,
            'description': self.description,
            'event_creator': self.event_creator,
            'photo': self.photo
        }

# LUCY: Keep User table for Sign Ins (revisit details later)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    # User information
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    created_events = db.relationship('Event', cascade='delete', secondary=event_user_table)
    password_digest = db.Column(db.String, nullable=False)

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.last_name = kwargs.get('last_name')
        self.first_name = kwargs.get('first_name')
        self.password_digest = bcrypt.hashpw(kwargs.get('password').encode('utf8'),
                                            bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        return {
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email,
            'id': self.id
        }

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + \
                                datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'),
                              self.password_digest)

    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return session_token == self.session_token and \
            datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        return update_token == self.update_token