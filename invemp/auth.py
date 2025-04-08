import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from invemp.db import get_cursor


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['type']
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
            return redirect(url_for('auth.register'))

        flash(error)

    return render_template('auth/register.html')

