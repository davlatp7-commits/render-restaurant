from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.secret_key = "supersecret"

    db.init_app(app)
    migrate.init_app(app, db)

    # Импорт моделей (чтобы они регистрировались)
    from app.models import dish, order, order_item, table

    # Импорт и регистрация блюпринтов
    from app.routes.client import client_bp
    from app.routes.admin import admin_bp
    from app.routes.waiter import waiter_bp

    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(waiter_bp)

    return app
