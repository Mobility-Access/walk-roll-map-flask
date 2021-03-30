from datetime import datetime

from flask import current_app

from app import db


types = [
    'micro_barriers',
    'safety_comfort_concerns',
    'missing_amenities',
    'incidents',
]

age = [
    '13-19',
    '20-29',
    '30-39',
    '40-49',
    '50-64',
    '65-79',
    '80+',
    '<13',
    'none'
]

yes_no_none = [
    'y',
    'n',
    'none'
]


class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reported = db.Column(db.DateTime, default=datetime.utcnow())
    type = db.Column(db.String(20))
    gender = db.Column(db.String(30))
    race = db.Column(db.String(50))
    age = db.Column(db.String(10))
    disability = db.Column(db.String(5))
    disability_type = db.Column(db.String(10))
    mobility_aid = db.Column(db.String(5))
    mobility_aid_type = db.Column(db.String(50))



