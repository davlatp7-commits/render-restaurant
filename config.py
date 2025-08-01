import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "postgresql://restaurant_2kc6_user:flgp8Ilot7yGCIifGiJfQ1VKaXY0RUwV@dpg-d26ep42li9vc7391og4g-a.oregon-postgres.render.com/restaurant_2kc6"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
