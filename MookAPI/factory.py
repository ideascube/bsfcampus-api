import os

from flask import Flask
from flask_login import LoginManager

def create_app(
        package_name,
        package_path=None,
        settings_override=None):

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

    # User authent
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from MookAPI.services import user_credentials
            return user_credentials.get(id=user_id)
        except:
            return None

    if package_path:
        from .helpers import register_blueprints
        register_blueprints(app, package_name, package_path)

    @app.after_request
    def after_request(response):
        response.headers.add('Accept-Ranges', 'bytes')
        return response

    if app.config.get('SERVER_TYPE', 'central') == 'central':
        from .admin import Admin
        from .admin.views import ProtectedFileAdmin
        admin = Admin()
        admin.init_app(app)

        path = app.config.get('UPLOAD_FILES_PATH')
        admin.add_view(ProtectedFileAdmin(path, name='Static Files', category="Misc", authorized_roles=('admin', 'contenu')))

    return app
