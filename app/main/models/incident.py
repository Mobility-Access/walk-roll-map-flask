from datetime import datetime

from flask import current_app

from app import db
from app.main.models.point import Point

required_incident_fields = [
    'incident_type',
    'incident_with',
    'injury_type',
    'involvement'
]

all_incident_fields = [
    'incident_type',
    'incident_with',
    'injury_type',
    'involvement'
]


class Incident(Point, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('point.id'), primary_key=True)
    incident_type = db.Column(db.String(10))
    incident_with = db.Column(db.String(50))
    injury_type = db.Column(db.String(50))
    involvement = db.Column(db.String(10))


    # Returns a subset of fields for display on the map.
    def to_small_dict(self):
        data = super().to_small_dict()
        data['incident_type'] = self.incident_type
        data['incident_with'] = self.incident_with
        return data


    # TODO: This should only be accessible by admins.
    # Returns a dictionary containing all fields. 
    def to_dict(self):
        data = super().to_dict()
        data['incident_type'] = self.incident_type
        data['incident_with'] = self.incident_with
        data['injury_type'] = self.injury_type
        data['involvement'] = self.involvement
        return data


    def from_dict(self, data):
        super().from_dict(data)
        for field in all_incident_fields:
            if field in data:
                setattr(self, field, data[field])



class IncidentTypes():
    incident_types = [
        'hit_by',
        'near_miss',
        'fall'
    ]


class IncidentWith():
    [
        'vehicle_right_turn',
        'vehicle_right_turn_red',
        'vehicle_left_turn',
        'vehicle_head_on',
        'vehicle_from_behind',
        'cyclist',
        'animal',
        'slipped',
        'tripped',
        'other'
    ]

class InjuryTypes():
    [
        'no_injury',
        'self_treatment',
        'family_doctor',
        'er_by_self',
        'er_by_ambulance',
        'hospitalized'
        'witness_no_injury',
        'witness_minor_injury',
        'witenss_ambulance'
    ]

class Involvement():
    [
        'self',
        'other',
        'witness'
    ]