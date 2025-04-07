import mysql.connector

from datetime import datetime

from flask import current_app, g


def get_conf():
    """Get a database config."""
    return current_app.config['DATABASE']

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)