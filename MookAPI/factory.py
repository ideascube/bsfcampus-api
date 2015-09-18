import os

from flask import Flask

def create_app(
        package_name,
        package_path=None,
        settings_override=None,
        register_security_blueprint=True):

    static_folder = os.path.dirname(os.path.realpath(__file__))
    static_folder = os.path.join(static_folder, '../static')
    app = Flask(
        package_name,
        instance_relative_config=True,
        static_folder=static_folder
    )

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

    from flask.ext.admin.contrib.fileadmin import FileAdmin
    path = app.config.get('UPLOAD_FILES_PATH')
    admin_ui.add_view(FileAdmin(path, name='Static Files'))


    return app
