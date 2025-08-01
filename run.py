from app import create_app, db
from flask_migrate import upgrade

app = create_app()

# Выполняем миграции автоматически при запуске
with app.app_context():
    upgrade()from flask_migrate import upgrade
upgrade()
ы
