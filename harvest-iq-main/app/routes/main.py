from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from datetime import datetime, timezone

# 1. Blueprint must be defined BEFORE the routes below use it
main_bp = Blueprint('main', __name__)

# ─── Language Switcher ──────────────────────────────────────────────────────

@main_bp.route('/set-lang/<lang>')
def set_language(lang):
    """Switch between English and Tagalog."""
    if lang in ('en', 'tl'):
        session['lang'] = lang
    # Added url_for to imports to prevent a NameError here
    return redirect(request.referrer or url_for('main.index'))


# ─── Context Processor ────────────────────────────────────────────────────────

@main_bp.app_context_processor
def inject_globals():
    """Inject global variables available in ALL templates."""
    return {
        # Using timezone-aware UTC for modern Python standards
        'now': datetime.now(timezone.utc),
    }


# ─── Main Routes ──────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    """Homepage — featured products, categories, top farmers."""
    featured = (
        Product.query
        .filter_by(is_available=True)
        .order_by(Product.views.desc())
        .limit(8)
        .all()
    )
    categories = Category.query.all()
    top_farmers = (
        User.query
        .filter_by(role='farmer', is_active=True)
        .limit(6)
        .all()
    )
    return render_template(
        'index.html',
        featured=featured,
        categories=categories,
        top_farmers=top_farmers,
    )


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


# ─── Error Handlers ───────────────────────────────────────────────────────────

@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500