import unittest

from app import create_app, db
from config import config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


if __name__ == '__main__':
    unittest.main(verbosity=2)