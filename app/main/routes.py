from datetime import datetime

from flask import current_app, jsonify, request
from sqlalchemy import func

from app import db
from app.main import bp
from app.main.models.amenity import Amenity, required_amenity_fields
from app.main.models.barrier import Barrier, required_barrier_fields
from app.main.models.concern import Concern, required_concern_fields
from app.main.models.hazard import Hazard, required_hazard_fields
from app.main.models.incident import Incident, required_incident_fields
from app.main.models.point import Point, required_point_fields

import app


@bp.route('/')
def index():
    rando = [
        {
            'name': "Darren",
            'occupation': 'developer'
        },
        {
            'name': 'Angela',
            'occupation': 'Regional Agrologist'
        }
    ]

    return jsonify(rando)


@bp.route('/api/point')
def point():
    bbox = request.args.get('bbox')
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        points = Point.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Point.geom))
    if page is None:
        points = Point.query.all()
    else:
        points = Point.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [incident.to_small_dict() for incident in points],
        'totalCount': Point.query.count()
    }
    return jsonify(data)


@bp.route('/api/amenity', methods=['GET', 'POST'])
def amenity():
    if request.method == 'POST':
        data = request.get_json() or {}
        data["type"] = "amenity"
        missing_fields = validate_amenity_data(data)
        if (len(missing_fields) > 0):
            return make_missing_fields_error(missing_fields)
        amenity = Amenity()
        amenity.from_dict(data)
        db.session.add(amenity)
        db.session.commit()
        response = jsonify(amenity.to_small_dict())
        response.status_code = 201
        return response

    # Handle GET request
    bbox = request.args.get('bbox')
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        amenities = Amenity.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Amenity.geom))
    if page is None:
        amenities = Amenity.query.all()
    else:
        amenities = Amenity.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [amenity.to_small_dict() for amenity in amenities],
        'totalCount': Amenity.query.count()
    }
    return jsonify(data)


@bp.route('/api/hazard', methods=['GET', 'POST'])
def hazard():
    if request.method == 'POST':
        data = request.get_json() or {}
        missing_fields = validate_hazard_data(data)
        if (len(missing_fields) > 0):
            return make_missing_fields_error(missing_fields)
        hazard = Hazard()
        hazard.from_dict(data)
        db.session.add(hazard)
        db.session.commit()
        response = jsonify(hazard.to_small_dict())
        response.status_code = 201
        return response

    # Handle GET request
    bbox = request.args.get('bbox')
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        hazards = Hazard.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Hazard.geom))
    if page is None:
        hazards = Hazard.query.all()
    else:
        hazards = Hazard.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [hazard.to_small_dict() for hazard in hazards],
        'totalCount': Hazard.query.count()
    }
    return jsonify(data)


@bp.route('/api/incident', methods=['GET', 'POST'])
def incident():
    if request.method == 'POST':
        data = request.get_json() or {}
        missing_fields = validate_incident_data(data)
        if (len(missing_fields) > 0):
            return make_missing_fields_error(missing_fields)
        incident = Incident()
        incident.from_dict(data)
        db.session.add(incident)
        db.session.commit()
        response = jsonify(incident.to_small_dict())
        response.status_code = 201
        return response

    # Handle GET request
    bbox = request.args.get('bbox')
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        incidents = Incident.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Incident.geom))
    if page is None:
        incidents = Incident.query.all()
    else:
        incidents = Incident.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [incident.to_small_dict() for incident in incidents],
        'totalCount': Incident.query.count()
    }
    return jsonify(data)


# Checks if the new Amenity contains all the fields required in order for use to save it to the database
def validate_amenity_data(data):
    missing_fields = validate_point_data(data)
    for field in required_amenity_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


# Checks if the new Barrier contains all the fields required in order for use to save it to the database
def validate_barrier_data(data):
    missing_fields = validate_point_data(data)
    for field in required_barrier_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


# Checks if the new Concern contains all the fields required in order for use to save it to the database
def validate_concern_data(data):
    missing_fields = validate_point_data(data)
    for field in required_concern_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


# Checks if the new Hazard contains all the fields required in order for use to save it to the database
def validate_hazard_data(data):
    missing_fields = validate_point_data(data)
    for field in required_hazard_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


# Checks if the new Incident contains all the fields required in order for use to save it to the database
def validate_incident_data(data):
    missing_fields = validate_point_data(data)
    for field in required_incident_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


# Checks if the fields required for a new Potin are present
def validate_point_data(data):
    missing_fields = []
    for field in required_point_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields


def make_missing_fields_error(fields):
    message = 'Required fields are missing.'
    print(len(fields))
    if len(fields) == 1:
        message = 'Required field is missing.'
    error = {
        'message': message,
        'missing_fields': ', '.join(fields)
    }
    return jsonify(error)
        