from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.utils.constants import DELIVERY_FEE, FREE_DELIVERY_THRESHOLD, PAYMENT_METHODS

cart_bp = Blueprint('cart', __name__)

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

@cart_bp.route('/')
def view_cart():
    cart = get_cart()
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.is_available:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    delivery_fee = 0 if total >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    grand_total = total + delivery_fee
    return render_template('cart/cart.html', items=items, total=total,
                           delivery_fee=delivery_fee, grand_total=grand_total,
                           payment_methods=PAYMENT_METHODS)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get('quantity', 1))
    if qty < 1 or qty > product.stock_quantity:
        flash('Invalid quantity.', 'danger')
        return redirect(request.referrer or url_for('products.product_detail', product_id=product_id))

    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    if cart[key] > product.stock_quantity:
        cart[key] = product.stock_quantity
    save_cart(cart)
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update', methods=['POST'])
def update_cart():
    cart = get_cart()
    for key, qty in request.form.items():
        if key.startswith('qty_'):
            product_id = key.replace('qty_', '')
            try:
                qty = int(qty)
                product = Product.query.get(int(product_id))
                if product and qty > 0:
                    cart[product_id] = min(qty, product.stock_quantity)
                elif qty <= 0:
                    cart.pop(product_id, None)
            except ValueError:
                pass
    save_cart(cart)
    flash('Cart updated.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))

    shipping_address = request.form.get('shipping_address', current_user.address or '').strip()
    payment_method = request.form.get('payment_method', 'cod')
    notes = request.form.get('notes', '').strip()

    if not shipping_address:
        flash('Please provide a shipping address.', 'danger')
        return redirect(url_for('cart.view_cart'))

    items_data = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if not product or not product.is_available or product.stock_quantity < qty:
            flash(f'"{product.name if product else "A product"}" is no longer available in requested quantity.', 'danger')
            return redirect(url_for('cart.view_cart'))
        subtotal = product.price * qty
        total += subtotal
        items_data.append({'product': product, 'qty': qty, 'price': product.price})

    delivery_fee = 0 if total >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    grand_total = total + delivery_fee

    order = Order(
        buyer_id=current_user.id,
        total_amount=grand_total,
        delivery_fee=delivery_fee,
        shipping_address=shipping_address,
        payment_method=payment_method,
        notes=notes,
        status='pending',
        payment_status='unpaid' if payment_method != 'cod' else 'pending',
    )
    db.session.add(order)
    db.session.flush()

    for item in items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            quantity=item['qty'],
            unit_price=item['price'],
        )
        item['product'].stock_quantity -= item['qty']
        db.session.add(order_item)

    db.session.commit()
    session.pop('cart', None)

    flash(f'Order #{order.id} placed successfully!', 'success')
    return redirect(url_for('orders.order_detail', order_id=order.id))