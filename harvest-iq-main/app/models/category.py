from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    name_tl = db.Column(db.String(100))  # Tagalog name
    icon = db.Column(db.String(50), default='🌿')
    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'