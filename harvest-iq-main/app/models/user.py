from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(db.String(20), nullable=False, default='buyer')
    status = db.Column(db.String(20), default='approved')

    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    # Farmer Address Fields
    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    barangay = db.Column(db.String(100))
    full_address = db.Column(db.Text)

    initial_products = db.Column(db.String(255))
    initial_price = db.Column(db.Float)

    profile_image = db.Column(db.String(255), default='default_profile.jpg')

    created_at = db.Column(db.DateTime, default=datetime.now)

    # =========================
    # PASSWORD METHODS
    # =========================
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # =========================
    # ROLE HELPERS
    # =========================
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_farmer(self):
        return self.role == "farmer"

    @property
    def is_buyer(self):
        return self.role == "buyer"

    def __repr__(self):
        return f"<User {self.username}>"
