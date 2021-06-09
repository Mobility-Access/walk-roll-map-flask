from datetime import datetime

from flask import current_app

from app import db
from app.main.models.point import Point

required_barrier_fields = [
    'barrier_detail',
    'barrier_subtype',
    'barrier_type'
]

all_barrier_fields = [
    'barrier_detail',
    'barrier_subtype',
    'barrier_type'
]

class Barrier(Point, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('point.id'), primary_key=True)
    barrier_detail = db.Column(db.String(50))
    barrier_subtype = db.Column(db.String(25))
    barrier_type = db.Column(db.String(25))


    # Returns a subset of fields for display on the map.
    def to_small_dict(self):
        data = super().to_small_dict()
        data['properties']['barrier_detail'] = self.barrier_detail
        data['properties']['barrier_subtype'] = self.barrier_subtype
        data['properties']['barrier_type'] = self.barrier_type
        return data


    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all fields. 
    def to_dict(self):
        data = super().to_dict()
        data['barrier_detail'] = self.barrier_detail
        data['barrier_subtype'] = self.barrier_subtype
        data['barrier_type'] = self.barrier_subtype
        return data


    def from_dict(self, data):
        super().from_dict(data)
        for field in all_barrier_fields:
            if field in data:
                setattr(self, field, data[field])


    def barrier_types():
        return [
            'environmental',
            'infrastructure',
            'obstruction'
        ]

    def  infrastructure_subtypes():
        return [
            'crossing',
            'intersection',
            'sidewalk',
        ]

    def obstruction_subtypes():
        return [
            'fixed',
            'transient'
        ]