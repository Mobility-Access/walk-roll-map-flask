from datetime import datetime

from flask import current_app, jsonify, request
from sqlalchemy import func

from app import db
from app.main import bp
from app.main.models.amenity import Amenity, required_amenity_fields
from app.main.models.barrier import Barrier, required_barrier_fields
from app.main.models.concern import Concern, required_concern_fields
from app.main.models.incident import Incident, required_incident_fields
from app.main.models.point import Point, required_point_fields


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
    if bbox is None:
        points = Point.query.all()
    else:
        split = bbox.split(',')
        points = Point.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 4326), Point.geom))
    data = [point.to_dict() for point in points]
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
    if bbox is None:
        amenities = Amenity.query.all()
    else:
        split = bbox.split(',')
        amenities = Amenity.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 4326), Amenity.geom))
    data = {
        'type': 'FeatureCollection',
        'features': [amenity.to_small_dict() for amenity in amenities]
    }
    
    return jsonify(data)


@bp.route('/api/barrier', methods=['GET', 'POST'])
def barrier():
    if request.method == 'POST':
        data = request.get_json() or {}
        missing_fields = validate_barrier_data(data)
        if (len(missing_fields) > 0):
            return make_missing_fields_error(missing_fields)
        barrier = Barrier()
        barrier.from_dict(data)
        db.session.add(barrier)
        db.session.commit()
        response = jsonify(barrier.to_small_dict())
        response.status_code = 201
        return response

    # Handle GET request
    bbox = request.args.get('bbox')
    if bbox is None:
        barriers = Barrier.query.all()
    else:
        split = bbox.split(',')
        barriers = Barrier.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 4326), Barrier.geom))
    data = {
        'type': 'FeatureCollection',
        'features': [barrier.to_small_dict() for barrier in barriers]
    }
    
    return jsonify(data)


@bp.route('/api/concern', methods=['GET', 'POST'])
def concern():
    if request.method == 'POST':
        data = request.get_json() or {}
        missing_fields = validate_concern_data(data)
        if (len(missing_fields) > 0):
            return make_missing_fields_error(missing_fields)
        concern = Concern()
        concern.from_dict(data)
        db.session.add(concern)
        db.session.commit()
        response = jsonify(concern.to_small_dict())
        response.status_code = 201
        return response

    # Handle GET request
    bbox = request.args.get('bbox')
    if bbox is None:
        concerns = Concern.query.all()
    else:
        split = bbox.split(',')
        concerns = Concern.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 4326), Concern.geom))
    data = {
        'type': 'FeatureCollection',
        'features': [concern.to_small_dict() for concern in concerns]
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
    if bbox is None:
        incidents = Incident.query.all()
    else:
        split = bbox.split(',')
        incidents = Incident.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 4326), Incident.geom))
    data = {
        'type': 'FeatureCollection',
        'features': [incident.to_small_dict() for incident in incidents]
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
        