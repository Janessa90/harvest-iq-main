from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models.product import Product

weigh_bp = Blueprint(
    "weigh",
    __name__,
    url_prefix="/weigh"
)


# ─────────────────────────────────────────────
# ADD WEIGHT / PRODUCT AUTO TAG
# ─────────────────────────────────────────────
@weigh_bp.route("/add_weight", methods=["POST"])
@login_required
def add_weight():

    # Ensure farmer only
    if not current_user.is_farmer:
        return jsonify({
            "error": "Only farmers allowed"
        }), 403

    data = request.json

    product_name = data.get("product_name")
    weight = data.get("weight")

    if not product_name or not weight:
        return jsonify({
            "error": "Missing data"
        }), 400

    # Create product entry (pending approval)
    product = Product(
        name=product_name,
        weight=weight,
        farmer_id=current_user.id,
        status="pending"
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Weight recorded, waiting admin approval"
    })
