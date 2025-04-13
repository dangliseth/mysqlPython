import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from invemp.db import get_cursor


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        c = get_cursor()
        c.execute('SELECT * FROM user_accounts WHERE id = %s', (user_id,))
        g.user = c.fetchone()
        c.close()

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user[3] != 'admin':
            return redirect(url_for('dashboard.view_table', table_name='items'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
@admin_required
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['type']
        dropdown_options = {account_type: ['admin', 'user']}
        c = get_cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif c.execute(
            'SELECT id FROM user_accounts WHERE username = %s', (username,)
        ) and c.fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            c.execute(
                'INSERT INTO user_accounts (username, password, account_type) VALUES (%s, %s, %s)',
                (username, generate_password_hash(password), account_type)
            )
            c.connection.commit()
            c.close()
            return redirect(url_for('auth.register', dropdown_options=dropdown_options))

        flash(error)

    return render_template('auth/register.html', dropdown_options=dropdown_options)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        c = get_cursor()
        error = None
        c.execute(
            'SELECT * FROM user_accounts WHERE username = %s', (username,)
        )
        user = c.fetchone()
        c.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            if user[3] == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('dashboard.view_table', table_name='items'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view