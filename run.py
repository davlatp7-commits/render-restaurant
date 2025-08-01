from flask_migrate import upgrade
from app import app

# Применение миграций при запуске (работает и в dev, и на Render)
upgrade()
