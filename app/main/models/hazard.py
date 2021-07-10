from datetime import datetime

from flask import current_app

from app import db
from app.main.models.point import Point

required_hazard_fields = [
    'hazard_subtype',
    'hazard_type'
]

all_hazard_fields = [
    'hazard_subtype',
    'hazard_type'
]

class Hazard(Point, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('point.id'), primary_key=True)
    hazard_subtype = db.Column(db.String(65))
    hazard_type = db.Column(db.String(35))

    # Returns a subset of fields for display on the map.
    def to_small_dict(self):
        data = super().to_small_dict()
        data['properties']['hazard_subtype'] = self.hazard_subtype
        data['properties']['hazard_type'] = self.hazard_type
        return data


    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all fields. 
    def to_dict(self):
        data = super().to_dict()
        data['hazard_subtype'] = self.hazard_subtype
        data['hazard_type'] = self.hazard_type
        return data


    def from_dict(self, data):
        super().from_dict(data)
        for field in all_hazard_fields:
            if field in data:
                setattr(self, field, data[field])