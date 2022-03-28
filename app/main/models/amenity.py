from datetime import datetime

from flask import current_app

from app import db
from app.main.models.point import Point

required_amenity_fields = [
    'amenity_type'
]

all_amenity_fields = [
    'amenity_type'
]

public_amenity_fields = [
    'amenity_type'
]

class Amenity(Point, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('point.id'), primary_key=True)
    amenity_type = db.Column(db.String(50))

    # Returns a subset of fields for display on the map.
    def to_small_dict(self):
        data = super().to_small_dict()
        data['properties']['amenity_type'] = self.amenity_type
        return data


    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all fields. 
    def to_dict(self):
        data = super().to_dict()
        data['amenity_type'] = self.amenity_type
        return data

    def to_open_data_dict(self):
        data = super().to_open_data_dict()
        data['amenity_type'] = self.amenity_type
        return data

    def from_dict(self, data):
        super().from_dict(data)
        for field in all_amenity_fields:
            if field in data:
                setattr(self, field, data[field])