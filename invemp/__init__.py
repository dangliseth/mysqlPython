"""
Flask app factory for invemp package.
"""

from flask import Flask, redirect, url_for

from invemp.dashboard_helpers import get_dropdown_options

from . import db, auth, dashboard_user, dashboard_admin


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        print("Loaded DB user:", app.config.get("MYSQL_DATABASE_USER"))
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

    @app.context_processor
    def inject_dropdown_options():
        return dict(get_dropdown_options=get_dropdown_options)

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard_user.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(dashboard_admin.bp)

    return app