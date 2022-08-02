from datetime import date, timedelta

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

public_hazard_fields = [
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


    def to_open_data_dict(self):
        data = super().to_open_data_dict()
        data['hazard_subtype'] = self.hazard_subtype
        data['hazard_type'] = self.hazard_type
        return data


    def from_dict(self, data):
        super().from_dict(data)
        for field in all_hazard_fields:
            if field in data:
                setattr(self, field, data[field])

    
    def is_expired(self):
        hazard_type = self.hazard_type.casefold()
        if hazard_type == "safety/comfort concern" or hazard_type == "crossing issue":
            # Safety/comfort concerns and crossing issues never expire automatically
            return False
        elif hazard_type == "weather related or seasonal":
            return self.is_expired_by_weather()
        else:
            # side walk infrastructure issue
            return self.is_expired_by_sidewalk()


    def is_expired_by_sidewalk(self):
        hazard_subtype = self.hazard_subtype.casefold()
        if hazard_subtype == "obstruction - vegetaion that narrows pathway":
            return self.is_expired_by_time(180)
        elif hazard_subtype == "obstruction - sign blocking path" or hazard_subtype == "obstruction - parked e-scooters/bicycles":
            return self.is_expired_by_time(30)
        elif hazard_subtype == "obstruction - garbage or recycling bins" or hazard_subtype == "obstruction - parked vehicles or delivery vans":
            return self.is_expired_by_time(7)
        elif hazard_subtype == "obstruction - inadequate or lack of safe detour for pedestrians":
            return self.is_expired_by_time(30)
        return False


    def is_expired_by_weather(self):
        hazard_subtype = self.hazard_subtype.casefold()
        if hazard_subtype == "ice" or hazard_subtype == "puddles":
            return self.is_expired_by_time(7)
        elif hazard_subtype == "leaves":
            return self.is_expired_by_time(30)
        elif hazard_subtype == "other":
            return self.is_expired_by_time(180)
        else:
            # hazard is snow which expires in 30 days and between March 31 and Nov 1
            if self.is_expired_by_time(30) == True:
                return True
            year = date.today().year
            no_snow_start = date(year, 4, 1)
            no_snow_end = date(year, 10, 31)
            return self.date.date() < no_snow_start or self.date.date() > no_snow_end

    
    def is_expired_by_time(self, interval):
        if ((self.date + timedelta(days=interval)).date() < date.today() ):
            return True
        return False

    
