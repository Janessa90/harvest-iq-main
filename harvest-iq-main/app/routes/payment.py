from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.order import Order
import stripe

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/process/<int:order_id>', methods=['GET', 'POST'])
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))

    if order.payment_method == 'cod':
        flash('Cash on Delivery selected. Please prepare exact change.', 'info')
        return redirect(url_for('orders.order_detail', order_id=order_id))

    if order.payment_method == 'card':
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        return render_template('payment/stripe.html', order=order,
                               pub_key=current_app.config['STRIPE_PUBLIC_KEY'])

    # GCash / Maya — display QR/instructions
    return render_template('payment/ewallet.html', order=order)

@payment_bp.route('/stripe/charge/<int:order_id>', methods=['POST'])
@login_required
def stripe_charge(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    token = request.form.get('stripeToken')
    try:
        charge = stripe.Charge.create(
            amount=int(order.total_amount * 100),
            currency='php',
            description=f'Harvest IQ Order #{order.id}',
            source=token,
        )
        order.payment_status = 'paid'
        order.payment_reference = charge.id
        order.status = 'confirmed'
        db.session.commit()
        flash('Payment successful!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order_id))
    except stripe.error.StripeError as e:
        flash(f'Payment failed: {e.user_message}', 'danger')
        return redirect(url_for('payment.process_payment', order_id=order_id))

@payment_bp.route('/confirm-ewallet/<int:order_id>', methods=['POST'])
@login_required
def confirm_ewallet(order_id):
    order = Order.query.get_or_404(order_id)
    ref = request.form.get('reference', '').strip()
    if ref:
        order.payment_reference = ref
        order.payment_status = 'paid'
        order.status = 'confirmed'
        db.session.commit()
        flash('Payment reference submitted. Order confirmed!', 'success')
    else:
        flash('Please enter a valid reference number.', 'danger')
    return redirect(url_for('orders.order_detail', order_id=order_id))
