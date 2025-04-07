import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

import mysql.connector
from invemp.db import get_conf


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        current_app.config['DATABASE']['user'] = username
        current_app.config['DATABASE']['password'] = password

        db_config = get_conf()
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        error = None
        cursor.execute(
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

