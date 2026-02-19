import os
from werkzeug.utils import secure_filename
from flask import current_app

from app import db
from app.models.user import User
from app.models.category import Category


# ─────────────────────────────────────────────
# IMAGE UPLOAD HELPER
# ─────────────────────────────────────────────
def save_image(file):

    if not file:
        return None

    filename = secure_filename(file.filename)

    upload_path = os.path.join(
        current_app.root_path,
        'static/uploads/products',
        filename
    )

    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    file.save(upload_path)

    return f"uploads/products/{filename}"


# ─────────────────────────────────────────────
# SEED DEFAULT CATEGORIES
# ─────────────────────────────────────────────
def seed_categories():

    default_categories = [
        "Vegetables",
        "Fruits",
        "Rice",
        "Root Crops",
        "Livestock",
        "Seafood"
    ]

    for name in default_categories:
        existing = Category.query.filter_by(name=name).first()

        if not existing:
            category = Category(name=name)
            db.session.add(category)

    db.session.commit()

    print("✅ Default categories checked/created.")


# ─────────────────────────────────────────────
# SEED DEFAULT ADMIN
# ─────────────────────────────────────────────
def seed_admin():

    admin = User.query.filter_by(username="admin").first()

    if not admin:

        admin = User(
            username="admin",
            email="admin@harvestiq.com",
            role="admin",
            full_name="System Admin",
            phone="09123456789",
            status="approved"
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("✅ Default admin created: admin / admin123")

    else:
        print("ℹ️ Admin already exists.")
