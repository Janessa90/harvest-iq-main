import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Define paths dynamically
# basedir = C:\Users\...\HARVEST IQ\config
basedir = os.path.abspath(os.path.dirname(__file__))
# project_root = C:\Users\...\HARVEST IQ
project_root = os.path.dirname(basedir)

class DevelopmentConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'harvest-iq-secret-dev-key-2024')
    
    # Absolute path to the database file
    db_path = os.path.join(project_root, 'data', 'farmers_marketplace.db')
    
    # We use f-string to ensure the path is absolute (starts with C:\)
    # This bypasses the SQLite "unable to open" error on Windows/OneDrive
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # Mail Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@harvestiq.ph')

    # Uploads
    UPLOAD_FOLDER = os.path.join(project_root, 'data')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

    # Pagination
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10

# --- Safety Check: Create folders if they don't exist ---
os.makedirs(os.path.join(project_root, 'data'), exist_ok=True)
os.makedirs(os.path.join(project_root, 'data'), exist_ok=True)