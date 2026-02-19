from app import db

def get_db():
    return db.session

def init_db(app):
    with app.app_context():
        db.create_all()
        