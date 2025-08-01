from app import db

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    weight = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(120))
    image_url = db.Column(db.String(255))  # <--- Добавлено поле
    is_available = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f"<Dish {self.name}>"
        