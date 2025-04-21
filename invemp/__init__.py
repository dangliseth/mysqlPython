import os

from flask import (Flask, redirect, url_for)



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        MYSQL_DATABASE_HOST='localhost',
        MYSQL_DATABASE_USER='app_user',
        MYSQL_DATABASE_PASSWORD='test',
        MYSQL_DATABASE_DB='inventory_database',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.after_request
    def add_cache_control(response):
        if 'Cache-Control' not in response.headers:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='icons/favicon/favicon.ico'))
    
    
    from . import db

    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')

    return app