from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

# Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    # If already logged in → redirect by role
    if current_user.is_authenticated:

        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))

        elif current_user.is_farmer:
            return redirect(url_for('users.dashboard'))

        else:
            return redirect(url_for('users.dashboard'))

    # LOGIN POST
    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        # VALIDATE USER
        if user and user.check_password(password):

            # Farmer approval check
            if user.role == "farmer" and user.status != "approved":
                flash(
                    "Ang iyong farmer account ay naghihintay pa ng approval mula sa admin.",
                    "warning"
                )
                return render_template('auth/login.html')

            login_user(user, remember=bool(remember))

            next_page = request.args.get('next')

            flash(
                f"Maligayang pagbabalik, {user.full_name or user.username}!",
                "success"
            )

            # 🔥 ROLE BASED REDIRECT
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))

            elif user.is_farmer:
                return redirect(next_page or url_for('users.dashboard'))

            else:  # buyer
                return redirect(next_page or url_for('users.dashboard'))

        else:
            flash("Maling username o password.", "danger")

    return render_template('auth/login.html')


# ─────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':

        role = request.form.get('role', 'buyer')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if password != confirm:
            flash('Hindi magtugma ang password.', 'danger')
            return render_template('auth/register.html')

        # =========================
        # BUYER
        # =========================
        if role == 'buyer':

            email = request.form.get('email', '').strip()

            if User.query.filter_by(username=email).first():
                flash('Ang email na ito ay gamit na.', 'danger')
                return render_template('auth/register.html')

            user = User(
                username=email,
                email=email,
                role='buyer',
                full_name=full_name,
                phone=phone,
                status='approved'
            )

        # =========================
        # FARMER
        # =========================
        elif role == 'farmer':

            username = request.form.get('username', '').strip()

            if User.query.filter_by(username=username).first():
                flash('Ang username na ito ay gamit na.', 'danger')
                return render_template('auth/register.html')

            user = User(
                username=username,
                email=f"{username}@farmer.local",
                role='farmer',
                full_name=full_name,
                phone=phone,
                province=request.form.get('province'),
                city=request.form.get('city'),
                barangay=request.form.get('barangay'),
                full_address=request.form.get('full_address'),
                initial_products=request.form.get('products'),
                initial_price=float(request.form.get('price') or 0),
                status='pending'
            )

        # SET PASSWORD
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Farmer waits approval
        if role == 'farmer':
            flash(
                "Matagumpay ang registration! Hintayin ang approval ng Admin bago mag-login.",
                "info"
            )
            return redirect(url_for('auth.login'))

        # Buyer auto login
        login_user(user)

        flash(
            "Account created! Maligayang pagdating sa Harvest IQ!",
            "success"
        )

        return redirect(url_for('users.dashboard'))

    return render_template('auth/register.html')


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Naka-logout ka na.', 'info')
    return redirect(url_for('main.index'))


# ─────────────────────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':
        flash("Password reset feature coming soon.", "info")
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')
