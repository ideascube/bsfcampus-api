from flask import Flask

def create_app(
        package_name,
        package_path,
        settings_override=None,
        register_security_blueprint=True):

    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('MookAPI.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    from .core import db
    db.init_app(app)

    from .helpers import register_blueprints
    register_blueprints(app, package_name, package_path)

    from .admin import admin
    admin.init_app(app)

    return app
