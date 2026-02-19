from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.category import Category
from app.utils.helpers import save_image

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products"
)

# ─────────────────────────────────────────────
# LIST PRODUCTS (BUYER SIDE)
# APPROVED ONLY
# ─────────────────────────────────────────────
@products_bp.route("/")
def list_products():

    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", "newest")
    organic = request.args.get("organic", type=bool)

    # 🔥 ONLY APPROVED PRODUCTS
    query = Product.query.filter_by(
        is_available=True,
        status="approved"
    )

    if category_id:
        query = query.filter_by(category_id=category_id)

    if organic:
        query = query.filter_by(is_organic=True)

    # Sorting
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "popular":
        query = query.order_by(Product.views.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(
        page=page,
        per_page=current_app.config.get("PRODUCTS_PER_PAGE", 8)
    )

    categories = Category.query.all()

    return render_template(
        "products/list.html",
        products=products,
        categories=categories,
        selected_category=category_id,
        sort=sort
    )


# ─────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────
@products_bp.route("/<int:product_id>")
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    # Prevent viewing unapproved
    if product.status != "approved":
        flash("Hindi available ang produktong ito.", "warning")
        return redirect(url_for("products.list_products"))

    product.views += 1
    db.session.commit()

    related = Product.query.filter_by(
        category_id=product.category_id,
        is_available=True,
        status="approved"
    ).filter(Product.id != product.id).limit(4).all()

    return render_template(
        "products/detail.html",
        product=product,
        related=related
    )


# ─────────────────────────────────────────────
# ADD PRODUCT (FARMER)
# AUTO PENDING
# ─────────────────────────────────────────────
@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():

    if current_user.role != "farmer":
        flash("Para lamang ito sa magsasaka.", "danger")
        return redirect(url_for("main.index"))

    categories = Category.query.all()

    if request.method == "POST":

        image_file = request.files.get("image")
        image_path = save_image(image_file) if image_file else "default_product.jpg"

        product = Product(
            farmer_id=current_user.id,
            category_id=int(request.form.get("category_id")),
            name=request.form.get("name"),
            description=request.form.get("description"),
            price=float(request.form.get("price", 0)),
            unit=request.form.get("unit", "kg"),
            stock_quantity=int(request.form.get("stock_quantity", 0)),
            min_order_quantity=int(request.form.get("min_order_quantity", 1)),
            is_organic="is_organic" in request.form,
            location=request.form.get("location"),
            image=image_path,

            # 🔥 ADMIN APPROVAL
            status="pending"
        )

        db.session.add(product)
        db.session.commit()

        flash(
            "Naipasa ang produkto. Hihintayin ang approval ng admin.",
            "info"
        )

        return redirect(url_for("users.dashboard"))

    return render_template(
        "products/add.html",
        categories=categories
    )


# ─────────────────────────────────────────────
# EDIT PRODUCT
# ─────────────────────────────────────────────
@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):

    product = Product.query.get_or_404(product_id)

    if product.farmer_id != current_user.id:
        flash("Hindi mo ito produkto.", "danger")
        return redirect(url_for("main.index"))

    categories = Category.query.all()

    if request.method == "POST":

        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price"))
        product.unit = request.form.get("unit")
        product.stock_quantity = int(request.form.get("stock_quantity"))
        product.category_id = int(request.form.get("category_id"))
        product.is_organic = "is_organic" in request.form
        product.is_available = "is_available" in request.form

        # Reset approval
        product.status = "pending"

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            product.image = save_image(image_file)

        db.session.commit()

        flash(
            "Na-update ang produkto. For admin approval ulit.",
            "info"
        )

        return redirect(url_for("users.dashboard"))

    return render_template(
        "products/edit.html",
        product=product,
        categories=categories
    )


# ─────────────────────────────────────────────
# DELETE PRODUCT
# ─────────────────────────────────────────────
@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):

    product = Product.query.get_or_404(product_id)

    if product.farmer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("main.index"))

    db.session.delete(product)
    db.session.commit()

    flash("Nabura ang produkto.", "success")

    return redirect(url_for("users.dashboard"))
