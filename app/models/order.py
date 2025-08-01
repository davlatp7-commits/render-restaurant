from app import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='новый')  # новый, принят, готов, завершён
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order #{self.id} - Стол {self.table_id}>"
