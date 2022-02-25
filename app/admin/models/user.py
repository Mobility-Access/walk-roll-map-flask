from app import db

from flask import current_app
import jwt
import time
from werkzeug.security import generate_password_hash, check_password_hash

import pdb


# Model and code adapted from Miguel Grinberg:
# https://blog.miguelgrinberg.com/post/restful-authentication-with-flask

class User(db.Model):
    __tablename__ = 'users'
    can_download = db.Column(db.Boolean, default=True, nullable=False)
    can_edit = db.Column(db.Boolean, default=False, nullable=False)
    email = db.Column(db.String(128), nullable=False)
    id = db.Column(db.Integer, primary_key = True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
    
    db.UniqueConstraint(username)


    def to_dict(self):
        data = {
            'canDownload': self.can_download,
            'canEdit': self.can_edit,
            'email': self.email,
            'id': self.id,
            'isAdmin': self.is_admin,
            'username': self.username
        }
        return data


    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def generate_auth_token(self, expires_in=3600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')


    @staticmethod
    def verify_auth_token(token):
        try:
            # pdb.set_trace()
            data = jwt.decode(token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])