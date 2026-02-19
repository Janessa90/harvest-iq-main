from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Product

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@users_bp.route("/dashboard")
@login_required
def dashboard():

    # 🔥 FARMER DASHBOARD
    if current_user.role == "farmer":

        products = Product.query.filter_by(
            farmer_id=current_user.id
        ).all()

        pending_count = Product.query.filter_by(
            farmer_id=current_user.id,
            status="pending"
        ).count()

        approved_count = Product.query.filter_by(
            farmer_id=current_user.id,
            status="approved"
        ).count()

        rejected_count = Product.query.filter_by(
            farmer_id=current_user.id,
            status="rejected"
        ).count()

        return render_template(
            "users/farmer_dashboard.html",
            products=products,
            pending_count=pending_count,
            approved_count=approved_count,
            rejected_count=rejected_count
        )

    # 🔥 BUYER DASHBOARD
    products = Product.query.filter_by(
        status="approved",
        is_available=True
    ).all()

    return render_template(
        "users/buyer_dashboard.html",
        products=products
    )


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────
@users_bp.route("/profile")
@login_required
def profile():

    return render_template(
        "users/profile.html",
        user=current_user
    )


# ─────────────────────────────────────────────
# MY PRODUCTS (FARMER)
# ─────────────────────────────────────────────
@users_bp.route("/my_products")
@login_required
def my_products():

    if current_user.role != "farmer":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    products = Product.query.filter_by(
        farmer_id=current_user.id
    ).all()

    return render_template(
        "users/my_products.html",
        products=products
    )
