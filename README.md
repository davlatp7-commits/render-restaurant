# Restaurant App

## 📦 Установка и запуск

1. Клонируй или разархивируй проект
2. Перейди в директорию проекта:
```
cd restaurant_app
```

3. Создай виртуальное окружение и активируй:
```
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate   # для Windows
```

4. Установи зависимости:
```
pip install -r requirements.txt
```

5. Укажи настройки БД в `config.py`, например:
```
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:yourpassword@localhost:5432/restaurant"
```

6. Инициализируй БД:
```
flask db init
flask db migrate
flask db upgrade
```

7. Запусти приложение:
```
flask run
```

## 🔗 Маршруты
- `/` — клиентское меню
- `/admin` — админка
- `/waiter` — панель официанта

