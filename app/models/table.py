from app import db

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"<Table {self.number}>"
