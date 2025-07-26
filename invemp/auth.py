"""
Authentication and authorization routes and helpers for invemp.
"""
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from invemp.db import get_cursor
from invemp.dashboard_helpers import get_preserved_args

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    # Idle timeout logic (15 minutes)
    timeout_seconds = 900
    last_activity = session.get('last_activity')
    now = int(__import__('time').time())
    if user_id is not None and last_activity is not None:
        if now - last_activity > timeout_seconds:
            session.clear()
            g.user = None
            flash('You have been logged out due to inactivity.')
            return redirect(url_for('auth.login'))
        else:
            session['last_activity'] = now
    if user_id is None:
        g.user = None
    else:
        try:
            c = get_cursor()
            c.execute('SELECT * FROM user_accounts WHERE id = %s', (user_id,))
            g.user = c.fetchone()
            c.close()
        except Exception as e:
            g.user = None
            print(f"Error loading user: {e}")

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user[3] != 'admin':
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
@admin_required
def register():
    dropdown_options = {'admin', 'user'}
    preserved_args = get_preserved_args()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['type']
        error = None
        try:
            c = get_cursor()
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
                return redirect(url_for('dashboard_user.index', table_name='user_accounts', **preserved_args))
            c.close()
        except Exception as e:
            error = f"Database error: {e}"
        flash(error)
    return render_template('auth/register.html', dropdown_options=dropdown_options, preserved_args=preserved_args)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('dashboard_user.index'))
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            c = get_cursor()
            error = None
            c.execute(
                'SELECT * FROM user_accounts WHERE BINARY username = %s', (username,)
            )
            user = c.fetchone()
            c.close()
            if user is None or not check_password_hash(user[2], password):
                error = 'Incorrect username or password. Please try again.'

            if error is None:
                session.clear()
                session['user_id'] = user[0]
                session['last_activity'] = int(__import__('time').time())
                response = redirect(url_for('index'))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            flash(error)
        except Exception as e:
            print(f"Error during login: {e}")
            flash(f"An error occurred during login. Please try again. {e}")
    response = make_response(render_template('auth/login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@bp.route('/logout')
def logout():
    session.clear()
    response = redirect(url_for('auth.login'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

@bp.route('/<int:id>/reset_password', methods=('GET', 'POST'))
@admin_required
def reset_password(id):
    preserved_args = get_preserved_args()
    preserved_args.pop('table_name', None)
    try:
        c = get_cursor()
        c.execute("SELECT * FROM user_accounts WHERE id = %s", (id,))
        entry = c.fetchone()
        c.close()
    except Exception as e:
        flash(f"Error fetching user: {e}")
        return redirect(url_for('dashboard_user.index', table_name='user_accounts', **preserved_args))
    error = None
    if request.method == 'POST':
        new_password = request.form.get('new-password', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()
        if not new_password or not confirm_password:
            error = "Both password fields are required."
        elif new_password != confirm_password:
            error = "Passwords must match!"
        if error is None:
            try:
                c = get_cursor()
                c.execute(
                    "UPDATE user_accounts SET password = %s WHERE id = %s",
                    (generate_password_hash(new_password), id)
                )
                c.connection.commit()
                c.close()
                flash("Password reset successful.")
                return redirect(url_for('dashboard_user.index', table_name='user_accounts', **preserved_args))
            except Exception as e:
                error = f"Database error: {e}"
        flash(error)
    return render_template('auth/reset_password.html', entry=entry, preserved_args=preserved_args, table_name='user_accounts')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view