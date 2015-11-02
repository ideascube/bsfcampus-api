from flask import abort, redirect, url_for, request

from flask.ext.admin.contrib.mongoengine import ModelView
# from flask_security import current_user
from flask.ext.admin.contrib.fileadmin import FileAdmin


class ProtectedAdminViewMixin:
    def is_accessible(self):
        return True
        # if not current_user.is_active or not current_user.is_authenticated:
        #     return False
        # if current_user.has_role("admin"):
        #     return True
        # return False

    # def _handle_view(self, name, **kwargs):
    #     if not self.is_accessible():
    #         if not current_user.is_anonymous:
    #             abort(403)
    #         else:
    #             return redirect(url_for('security.login', next=request.url))


class ProtectedFileAdmin(ProtectedAdminViewMixin, FileAdmin):
    pass


class ProtectedModelView(ProtectedAdminViewMixin, ModelView):
    pass
