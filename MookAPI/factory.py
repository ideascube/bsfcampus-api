from flask import Flask

def create_app(
        package_name,
        package_path=None,
        settings_override=None,
        register_security_blueprint=True):

    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('MookAPI.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    from .core import db
    db.init_app(app)

    if package_path:
        from .helpers import register_blueprints
        register_blueprints(app, package_name, package_path)

    @app.after_request
    def after_request(response):
        response.headers.add('Accept-Ranges', 'bytes')
        return response

    from .admin_ui import admin_ui
    admin_ui.init_app(app)

    return app
