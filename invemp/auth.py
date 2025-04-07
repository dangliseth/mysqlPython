import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

import mysql.connector
from invemp.db import get_db, get_cursor


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """register in a user."""
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
            'SELECT id FROM user_accounts WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            c.execute(
                'INSERT INTO user_accounts (username, password, account_type,) VALUES (%s, %s, %s)',
                (username, generate_password_hash(password), account_type)
            )
            c.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

