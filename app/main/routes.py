from datetime import datetime

from flask import current_app, jsonify, request

# from app import db
from app.main import bp

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