from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from app.services.auth_service import AuthService
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if AuthService.authenticate(username, password):
            return redirect(url_for('company.index'))
        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    AuthService.logout()
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/current-user')
@login_required
def get_current_user():
    name = AuthService.get_user_display_name()

    group = AuthService.get_user_group()

    response = {
        'name': name,
        'group': group
    }

    return jsonify(response)