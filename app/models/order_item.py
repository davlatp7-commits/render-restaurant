from app import db
from app.models.dish import Dish

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    dish = db.relationship("Dish")  # добавляем связь

    def __repr__(self):
        return f"<OrderItem: {self.dish.name} x{self.quantity}>"
