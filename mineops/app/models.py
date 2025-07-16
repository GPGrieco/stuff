from datetime import datetime
from . import db

class Patrol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    area = db.Column(db.String(120))
    notes = db.Column(db.Text)
    checklist = db.Column(db.Text)
    photo = db.Column(db.String(255))

class Hazard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    severity = db.Column(db.String(50))
    status = db.Column(db.String(50))
    photo = db.Column(db.String(255))
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment = db.Column(db.String(120))
    issue = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    photo = db.Column(db.String(255))
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

class TrailCam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120))
    filename = db.Column(db.String(255))
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
