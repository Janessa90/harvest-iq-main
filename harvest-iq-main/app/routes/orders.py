from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.utils.constants import DELIVERY_FEE, FREE_DELIVERY_THRESHOLD

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@login_required
def my_orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(buyer_id=current_user.id)\
                        .order_by(Order.created_at.desc())\
                        .paginate(page=page, per_page=current_app.config['ORDERS_PER_PAGE'])
    return render_template('orders/my_orders.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != current_user.id and not current_user.is_farmer:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('orders/detail.html', order=order)

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))
    if order.status in ('pending', 'confirmed'):
        order.status = 'cancelled'
        # Restore stock
        for item in order.items:
            item.product.stock_quantity += item.quantity
        db.session.commit()
        flash('Order cancelled.', 'info')
    else:
        flash('This order cannot be cancelled.', 'danger')
    return redirect(url_for('orders.order_detail', order_id=order_id))

@orders_bp.route('/farmer/manage')
@login_required
def farmer_orders():
    if not current_user.is_farmer:
        flash('Only farmers can view this page.', 'danger')
        return redirect(url_for('main.index'))
    # Get orders containing the farmer's products
    farmer_product_ids = [p.id for p in current_user.products]
    order_ids = db.session.query(OrderItem.order_id)\
                          .filter(OrderItem.product_id.in_(farmer_product_ids)).distinct().all()
    order_ids = [o[0] for o in order_ids]
    orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all()
    return render_template('orders/farmer_orders.html', orders=orders)

@orders_bp.route('/farmer/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_farmer:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid_statuses = ['confirmed', 'processing', 'shipped', 'delivered']
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    return redirect(url_for('orders.farmer_orders'))