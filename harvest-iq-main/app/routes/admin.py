from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Product
from app import db

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

# ==============================
# ADMIN DASHBOARD
# ==============================
@admin_bp.route('/dashboard')
@login_required
def dashboard():

    if not current_user.is_admin:
        flash("Admin access only.", "danger")
        return redirect(url_for('main.index'))

    pending_products = Product.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        'admin/dashboard.html',
        products=pending_products
    )


# ==============================
# APPROVE
# ==============================
@admin_bp.route('/approve/<int:product_id>')
@login_required
def approve_product(product_id):

    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(product_id)
    product.status = "approved"

    db.session.commit()

    flash("Product approved.", "success")
    return redirect(url_for('admin.dashboard'))


# ==============================
# REJECT
# ==============================
@admin_bp.route('/reject/<int:product_id>')
@login_required
def reject_product(product_id):

    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(product_id)
    product.status = "rejected"

    db.session.commit()

    flash("Product rejected.", "warning")
    return redirect(url_for('admin.dashboard'))
