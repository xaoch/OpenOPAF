from . import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d") +" "+ value.strftime("%H:%M:%S")

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    presId = db.Column(db.String(100), unique=True)
    presenter =db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    gaze = db.Column(db.Integer)
    posture = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    fp = db.Column(db.Integer)
    slides= db.Column(db.Boolean)
    fs = db.Column(db.Integer)
    tl = db.Column(db.Integer)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'presId': self.presId,
            'presenter': self.presenter,
            'date': dump_datetime(self.date),
            'gaze': self.gaze,
            'posture':self.posture,
            'volume': self.volume,
            'speed': self.speed,
            'fp': self.fp,
            'slides': self.slides,
            'fs': self.fs,
            'tl': self.tl
        }