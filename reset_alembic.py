from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.session.commit()
        print("✅ Таблица alembic_version успешно удалена.")
    except Exception as e:
        print(f"❌ Ошибка при удалении таблицы alembic_version: {e}")
