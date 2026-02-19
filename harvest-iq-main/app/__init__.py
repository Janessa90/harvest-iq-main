from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from datetime import datetime
from config.development import DevelopmentConfig

# ─── Initialize Extensions ─────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
socketio = SocketIO()
migrate = Migrate()

# ─── Application Factory ───────────────────────────
def create_app(config=DevelopmentConfig):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)

    # ─── Init Extensions ───────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # ─── Flask-Login Config ────────────────────────
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # ─── Register Blueprints ───────────────────────
    # Siguraduhin na 'auth.login' ay tumutugma sa url_prefix='/auth'
# ─── Register Blueprints ───────────────────────
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.search import search_bp
    from app.routes.cart import cart_bp
    from app.routes.payment import payment_bp
    from app.routes.messages import messages_bp
    from app.routes.main import main_bp
    from app.routes.weighing import weigh_bp


    app.register_blueprint(auth_bp, url_prefix='/auth')  # ✅ ONLY ONCE
    app.register_blueprint(weigh_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(admin_bp)
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(main_bp)
    


    # ─── Socket.IO Events ──────────────────────────
    from app import socketio_events

    # ─── Context Processors ────────────────────────
    @app.context_processor
    def inject_globals():
        from app.locales import get_locale
        lang = session.get('lang', 'en')

        unread_count = 0
        if current_user.is_authenticated:
            from app.models.message import Conversation
            conversations = Conversation.query.filter(
                (Conversation.buyer_id == current_user.id) |
                (Conversation.farmer_id == current_user.id)
            ).all()
            unread_count = sum(c.unread_count(current_user.id) for c in conversations)

        return {
            't': get_locale(lang),
            'lang': lang,
            'now': datetime.now(), # Gamitin ang local time para sa thesis
            'unread_messages': unread_count
        }

    # ─── Database Auto-Create ──────────────────────
    with app.app_context():

        db.create_all()

        from app.utils.helpers import seed_categories, seed_admin

        seed_categories()
        seed_admin()

    return app
