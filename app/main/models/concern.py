from datetime import datetime

from flask import current_app

from app import db
from app.main.models.point import Point

required_concern_fields = [
    'concern_type',
    'concern_with'
]

all_concern_fields = [
    'concern_type',
    'concern_with'
]

class Concern(Point, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('point.id'), primary_key=True)
    concern_type = db.Column(db.String(50))
    concern_with = db.Column(db.String(50))

    # Returns a subset of fields for display on the map.
    def to_small_dict(self):
        data = super().to_small_dict()
        data['concern_type'] = self.concern_type
        data['concern_with'] = self.concern_with
        return data


    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all fields. 
    def to_dict(self):
        data = super().to_dict()
        data['concern_type'] = self.concern_type
        data['concern_with'] = self.concern_with
        return data


    def from_dict(self, data):
        super().from_dict(data)
        for field in all_concern_fields:
            if field in data:
                setattr(self, field, data[field])