import os

from flaskext.mysql import MySQL

from flask import current_app, g


mysql = MySQL()
def init_db():
    db = get_db()

def get_db():
    """Get a connection to the database. If a connection already exists, return it."""
    if 'db' not in g:
        g.db = mysql.connect()
    return g.db

def get_cursor():
    """Get a cursor from the database connection."""
    db = get_db()
    return db.cursor()

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    mysql.init_app(app)
    app.teardown_appcontext(close_db)