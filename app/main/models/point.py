from datetime import datetime, timezone

from flask import current_app
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.sql import func

from app import db

import pdb


types = [
    'micro_barrier',
    'safety_comfort_concern',
    'missing_amenity',
    'incident',
]

yes_no_none = [
    'y',
    'n',
    'none'
]

required_point_fields = [
    'birth_year',
    'date',
    'description',
    'disability',
    'gender',
    'geom',
    'race',
    'type'
]

all_point_fields = [
    'birth_year',
    'description',
    'date',
    'date_reported',
    'disability',
    'disability_type',
    'gender',
    'geom',
    'mobility_aid',
    'mobility_aid_type',
    'race',
    'type'
]


class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birth_year = db.Column(db.Integer, default=-1)
    date = db.Column(db.DateTime)
    date_reported = db.Column(db.DateTime, server_default=func.now())
    description = db.Column(db.String(500))
    disability = db.Column(db.String(5))
    disability_type = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    geom = db.Column(Geometry(geometry_type='POINT', srid=4326))
    mobility_aid = db.Column(db.String(5))
    mobility_aid_type = db.Column(db.String(50))
    race = db.Column(db.String(50))
    type = db.Column(db.String(20))


    # Returns a subset of Point fields for display on the map.
    def to_small_dict(self):
        geom = to_shape(self.geom)
        coords = [geom.x, geom.y]
        dateInMilliseconds = datetime.timestamp(self.date) * 1000
        # data = {
        #     'id': self.id,
        #     'date': dateInMilliseconds,
        #     'description': self.description,
        #     'geom': coords,
        # }
        data = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': coords,
            },
            'properties': {
                'id': self.id,
                'date': dateInMilliseconds,
                'description': self.description,
            }
        }
        return data
        
    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all Point fields. 
    def to_dict(self):
        geom = to_shape(self.geom)
        coords = [geom.y, geom.x]
        dateInMilliseconds = datetime.timestamp(self.date) * 1000
        data = {
            'id': self.id,
            'birth_year': self.birth_year,
            'date': dateInMilliseconds,
            'date_reported': self.reported,
            'description': self.description,
            'disability': self.disability,
            'disability_type': self.disability_type,
            'gender': self.gender,
            'geom': coords,
            'mobility_aid': self.mobility_aid,
            'mobility_aid_type': self.mobility_aid_type,
            'race': self.race,
            'type': self.type
        }
        return data


    def from_dict(self, data):
        for field in all_point_fields:
            if field in data:
                if field == 'date':
                    dateInSeconds = datetime.utcfromtimestamp(data[field] / 1000)
                    setattr(self, field, dateInSeconds)
                elif field == 'geom' and len(data[field]) == 2:
                    coords = data[field]
                    setattr(self, field, f'POINT({coords[0]} {coords[1]})')
                else:
                    setattr(self, field, data[field])
