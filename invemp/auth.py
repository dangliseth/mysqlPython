import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from invemp.db import get_cursor


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c = get_cursor()
        error = None
        c.execute(
            'SELECT * FROM mysql.user WHERE user = %s', (username,)
        )
        user = cursor.fetchone()
        cursor.close()


        if user is None:
            error = 'Incorrect username.'
        elif password != user['password']:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            print('Logged in successfully.')


        flash(error)

    return render_template('auth/login.html')

