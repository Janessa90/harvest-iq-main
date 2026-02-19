from flask import Blueprint, render_template, request
from app.models.product import Product
from app.models.category import Category
from app.utils.validators import sanitize_search

search_bp = Blueprint('search', __name__)

@search_bp.route('/')
def search():
    q = sanitize_search(request.args.get('q', ''))
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    region = request.args.get('region', '')
    organic = request.args.get('organic', '')
    sort = request.args.get('sort', 'relevance')
    page = request.args.get('page', 1, type=int)

    query = Product.query.filter_by(is_available=True)

    if q:
        query = query.filter(
            Product.name.ilike(f'%{q}%') | Product.description.ilike(f'%{q}%')
        )
    if category_id:
        query = query.filter_by(category_id=category_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if region:
        query = query.filter(Product.location.ilike(f'%{region}%'))
    if organic == '1':
        query = query.filter_by(is_organic=True)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    results = query.paginate(page=page, per_page=12)
    categories = Category.query.all()
    return render_template('search/results.html', results=results, q=q,
                           categories=categories, selected_category=category_id,
                           sort=sort, organic=organic)