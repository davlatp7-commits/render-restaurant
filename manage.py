from flask import Flask
from flask_migrate import Migrate, upgrade
from app import db, create_app

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    with app.app_context():
        upgrade()
