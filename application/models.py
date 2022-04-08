from . import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class JsonModel(object):
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Presentation(db.Model,JsonModel):
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