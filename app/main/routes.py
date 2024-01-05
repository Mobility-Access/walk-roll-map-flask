from datetime import datetime
from xmlrpc.client import boolean

from flask import current_app, json, jsonify, request, Response
from sqlalchemy import func

from app import db
from app.main import bp
from app.main.models.amenity import Amenity, public_amenity_fields, required_amenity_fields
from app.main.models.barrier import Barrier, required_barrier_fields
from app.main.models.concern import Concern, required_concern_fields
from app.main.models.hazard import Hazard, public_hazard_fields, required_hazard_fields
from app.main.models.incident import Incident, public_incident_fields, required_incident_fields
from app.main.models.point import Point, public_point_fields, required_point_fields

import app

import csv
import datetime
import io
import json
import os

import pdb


def _create_export_response(content, name, format):
    if format == 'json' or format == 'geojson':
        mimetype = 'application/json'
    else:
        mimetype = 'text/csv'
    return Response(content,
        mimetype=mimetype,
        headers={'Content-Disposition': f'attachment;filename={name}.{format}'})


def _filter_by_visibility(reports):
    visible_reports = []
    for report in reports:
        if report.is_visible():
            visible_reports.append(report)
    return visible_reports


def _filter_amenities(amenities):
    return _filter_by_visibility(amenities)


def _filter_expired_hazards(visible_hazards):
    non_expired_hazards = []
    for hazard in visible_hazards:
        if not hazard.is_expired():
            non_expired_hazards.append(hazard)
    return non_expired_hazards


def _filter_hazards(hazards):
    visible_hazards = _filter_by_visibility(hazards)
    non_expired_hazards = _filter_expired_hazards(visible_hazards)
    return non_expired_hazards


def _filter_incidents(incidents):
    return _filter_by_visibility(incidents)


@bp.route('/')
def index():
    rando = [
    ]

    return jsonify(rando)

@bp.route('/swagger.json')
def swagger():
    json_url = os.path.join(current_app.root_path, "swagger.json")
    data = json.load(open(json_url))
    return jsonify(data)


@bp.route('/point')
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


@bp.route('/amenity', methods=['GET', 'POST'])
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
    filter = request.args.get('filter', default=False, type=boolean)
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        amenities = Amenity.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Amenity.geom))
    if page is None:
        amenities = Amenity.query.all()
    else:
        amenities = Amenity.query.paginate(page, rows, False).items
    if filter == True:
        amenities = _filter_amenities(amenities)
    data = {
        'type': 'FeatureCollection',
        'features': [amenity.to_small_dict() for amenity in amenities],
        'totalCount': Amenity.query.count()
    }
    return jsonify(data)


@bp.route('/amenity/export', methods = ['GET'])
def amenity_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    amenities = Amenity.query.all()
    amenities_array = [amenity.to_open_data_dict() for amenity in amenities]
    if format == 'geojson':
        geojson = {
            'type': 'FeatureCollection',
            'features': amenities_array,
            'totalCount': Amenity.query.count()
        }
        content = json.dumps(geojson)
    elif format == 'json':
        content = json.dumps(amenities_array)
    else:
        all_fields = public_point_fields + public_amenity_fields
        string_io = io.StringIO()
        csv_writer = csv.writer(string_io)
        csv_writer.writerow(all_fields)
        for amenity in amenities_array:
            line = []
            for field in all_fields:
                if field == 'date' or field == 'date_reported':
                    value = datetime.datetime.utcfromtimestamp(amenity[field]/1000).strftime('%Y-%m-%d %H:%M:%S')
                    line.append(value)
                else:
                    line.append(amenity[field])
            csv_writer.writerow(line)
        content = string_io.getvalue()
    return _create_export_response(content, 'amenity', format)


@bp.route('/hazard', methods=['GET', 'POST'])
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
    filter = request.args.get('filter', default=False, type=boolean)
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        hazards = Hazard.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Hazard.geom))
    if page is None:
        hazards = Hazard.query.all()
    else:
        hazards = Hazard.query.paginate(page, rows, False).items
    if filter == True:
        hazards = _filter_hazards(hazards)
    data = {
        'type': 'FeatureCollection',
        'features': [hazard.to_small_dict() for hazard in hazards],
        'totalCount': Hazard.query.count()
    }
    return jsonify(data)


@bp.route('/hazard/export', methods = ['GET'])
def hazard_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    hazards = Hazard.query.all()
    hazards_array = [hazard.to_open_data_dict() for hazard in hazards]
    if format == 'geojson':
        geojson = {
            'type': 'FeatureCollection',
            'features': hazards_array,
            'totalCount': Hazard.query.count()
        }
        content = json.dumps(geojson)
    elif format == 'json':
        content = json.dumps(hazards_array)
    else:
        all_fields = public_point_fields + public_hazard_fields
        string_io = io.StringIO()
        csv_writer = csv.writer(string_io)
        csv_writer.writerow(all_fields)
        for hazard in hazards_array:
            line = []
            for field in all_fields:
                if field == 'date' or field == 'date_reported':
                    value = datetime.datetime.utcfromtimestamp(hazard[field]/1000).strftime('%Y-%m-%d %H:%M:%S')
                    line.append(value)
                else:
                    line.append(hazard[field])
            csv_writer.writerow(line)
        content = string_io.getvalue()
    return _create_export_response(content, 'hazard', format)


@bp.route('/incident', methods=['GET', 'POST'])
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
    filter = request.args.get('filter', default=False, type=boolean)
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if bbox:
        split = bbox.split(',')
        incidents = Incident.query.filter(func.ST_Contains(func.ST_MakeEnvelope(split[0], split[1], split[2], split[3], 3857), Incident.geom))
    if page is None:
        incidents = Incident.query.all()
    else:
        incidents = Incident.query.paginate(page, rows, False).items
    if filter == True:
        incidents = _filter_incidents(incidents)
    data = {
        'type': 'FeatureCollection',
        'features': [incident.to_small_dict() for incident in incidents],
        'totalCount': Incident.query.count()
    }
    return jsonify(data)


@bp.route('/incident/export', methods = ['GET'])
def incident_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    incidents = Incident.query.all()
    incidents_array = [incident.to_open_data_dict() for incident in incidents]
    if format == 'geojson':
        geojson = {
            'type': 'FeatureCollection',
            'features': incidents_array,
            'totalCount': Incident.query.count()
        }
        content = json.dumps(geojson)
    elif format == 'json':
        content = json.dumps(incidents_array)
    else:
        all_fields = public_point_fields + public_incident_fields
        string_io = io.StringIO()
        csv_writer = csv.writer(string_io)
        csv_writer.writerow(all_fields)
        for incident in incidents_array:
            line = []
            for field in all_fields:
                if field == 'date' or field == 'date_reported':
                    value = datetime.datetime.utcfromtimestamp(incident[field]/1000).strftime('%Y-%m-%d %H:%M:%S')
                    line.append(value)
                else:
                    line.append(incident[field])
            csv_writer.writerow(line)
        content = string_io.getvalue()
    return _create_export_response(content, 'incident', format)


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
        