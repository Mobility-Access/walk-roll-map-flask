from flask import abort, g, jsonify, request, Response
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import func
from sqlalchemy.sql.expression import false

import csv
import datetime
import io
import json

from app import db
from app.admin import bp
from app.main.models.amenity import Amenity, all_amenity_fields
from app.main.models.hazard import Hazard, all_hazard_fields
from app.main.models.incident import Incident, all_incident_fields
from app.main.models.point import all_point_fields
from app.admin.models.user import User
import app


auth = HTTPBasicAuth()


def _create_export_response(content, name, format):
    if format == 'json' or format == 'geojson':
        mimetype = 'application/json'
    else:
        mimetype = 'text/csv'
    return Response(content,
        mimetype=mimetype,
        headers={'Content-Disposition': f'attachment;filename={name}.{format}'})


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@bp.route('/admin/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username })


@bp.route('/admin/password', methods = ['POST'])
@auth.login_required
def reset_password():
    new_password = request.json.get('password')
    if new_password is None:
        abort(400)
    user = g.user
    user.hash_password(new_password)
    db.session.commit()
    return jsonify({ 'username': user.username }) 


@bp.route('/admin/token', methods = ['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(3600)
    return jsonify({ 'token': token, 'duration': 3600 })


@bp.route('/admin/user', methods = ["GET"])
def get_user():
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


@bp.route('/admin/user/<username>', methods = ['DELETE', 'GET'])
def manage_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'data': { 'user': ''}, 'success': False})

    if request.method == 'GET':
        user_data = { 'username': user.username, 'id': user.id, 'hash': user.password_hash}
        return jsonify({'data': { 'user': user_data }, 'success': True })
    db.session.delete(user)
    db.session.commit()
    return jsonify({'data': { 'user': ''}, 'success': True })


@bp.route('/admin/amenity/export', methods = ['GET'])
# @auth.login_required
def amenity_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    amenities = Amenity.query.all()
    amenities_array = [amenity.to_dict() for amenity in amenities]
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
        all_fields = ['id'] + all_amenity_fields + all_point_fields
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



@bp.route('/admin/amenity/<id>', methods = ['DELETE', 'GET', 'OPTIONS', 'POST'])
# @auth.login_required
def amenity(id):
    amenity = Amenity.query.filter_by(id=id).first()
    data = {}
    if request.method == 'DELETE':
        if amenity is None:
            data = {'success': False, 'message': 'Report ID does not exist.'}
        else:
            db.session.delete(amenity)
            db.session.commit()
            data = { 'success': True }  
    elif request.method == 'GET':
        if amenity is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            data = { 'success': True, 'feature': amenity.to_dict() }
    elif request.method == 'POST':
        if amenity is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            json_data = request.get_json()
            print(json_data)
            amenity.from_dict(json_data)
            db.session.commit()
            data = { 'feature': amenity.to_dict(), 'success': True }
    return jsonify(data)


@bp.route('/admin/hazard/export', methods = ['GET'])
# @auth.login_required
def hazard_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    hazards = Hazard.query.all()
    hazards_array = [hazard.to_dict() for hazard in hazards]
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
        all_fields = ['id'] + all_hazard_fields + all_point_fields
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


@bp.route('/admin/hazard/<id>', methods = ['DELETE', 'GET', 'OPTIONS', 'POST'])
# @auth.login_required
def hazard(id):
    hazard = Hazard.query.filter_by(id=id).first()
    data = {}
    if request.method == 'DELETE':
        if hazard is None:
            data = {'success': False, 'message': 'Report ID does not exist.'}
        else:
            db.session.delete(hazard)
            db.session.commit()
            data = { 'success': True }  
    elif request.method == 'GET':
        if hazard is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            data = { 'success': True, 'feature': hazard.to_dict() }
    elif request.method == 'POST':
        if hazard is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            json_data = request.get_json()
            print(json_data)
            hazard.from_dict(json_data)
            db.session.commit()
            data = { 'feature': hazard.to_dict(), 'success': True }
    return jsonify(data)


@bp.route('/admin/incident/export', methods = ['GET'])
# @auth.login_required
def incident_export():
    format = request.args.get('format')
    if format != 'json' and format != 'geojson':
        format = 'csv'
    incidents = Incident.query.all()
    incidents_array = [incident.to_dict() for incident in incidents]
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
        all_fields = ['id'] + all_incident_fields + all_point_fields
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


@bp.route('/admin/incident/<id>', methods = ['DELETE', 'GET', 'OPTIONS', 'POST'])
# @auth.login_required
def incident(id):
    incident = Incident.query.filter_by(id=id).first()
    data = {}
    if request.method == 'DELETE':
        if incident is None:
            data = {'success': False, 'message': 'Report ID does not exist.'}
        else:
            db.session.delete(incident)
            db.session.commit()
            data = { 'success': True }  
    elif request.method == 'GET':
        if incident is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            data = { 'success': True, 'feature': incident.to_dict() }
    elif request.method == 'POST':
        if incident is None:
            data = { 'success': False, 'message': 'Report ID does not exist.' }
        else:
            json_data = request.get_json()
            print(json_data)
            incident.from_dict(json_data)
            db.session.commit()
            data = { 'feature': incident.to_dict(), 'success': True }
    return jsonify(data)


@bp.route('/admin/amenity', methods = ['GET'])
# @auth.login_required
def get_amenities():
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if page is None:
        amenities = Amenity.query.all()
    else:
        amenities = Amenity.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [amenity.to_dict() for amenity in amenities],
        'totalCount': Amenity.query.count()
    }
    return jsonify(data)


@bp.route('/admin/incident', methods = ['GET'])
# @auth.login_required
def get_incidents():
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if page is None:
        incidents = Incident.query.all()
    else:
        incidents = Incident.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [incident.to_dict() for incident in incidents],
        'totalCount': Incident.query.count()
    }
    return jsonify(data)


@bp.route('/admin/hazard', methods = ['GET'])
# @auth.login_required
def get_hazards():
    page = request.args.get('page', type=int)
    rows = request.args.get('rows', app.Config.POINTS_PER_PAGE, type=int)
    if page is None:
        hazards = Hazard.query.all()
    else:
        hazards = Hazard.query.paginate(page, rows, False).items
    data = {
        'type': 'FeatureCollection',
        'features': [hazard.to_dict() for hazard in hazards],
        'totalCount': Hazard.query.count()
    }
    return jsonify(data)

