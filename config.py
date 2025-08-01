import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "postgresql://postgres:5209908d@localhost:5432/restaurant"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
