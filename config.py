import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = "secret"
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/walkrollmap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False