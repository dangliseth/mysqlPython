from flask import (Flask, redirect, url_for)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

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
    
    from invemp.dashboard_helpers import get_dropdown_options
    @app.context_processor
    def inject_dropdown_options():
        return dict(get_dropdown_options=get_dropdown_options)
    
    
    from . import db

    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard_user
    app.register_blueprint(dashboard_user.bp)
    app.add_url_rule('/', endpoint='index')

    from . import dashboard_admin
    app.register_blueprint(dashboard_admin.bp)

    return app