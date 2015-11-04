from wtforms import ValidationError

from flask import abort, redirect, url_for, request

from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import BaseView, expose
# from flask_security import current_user


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


def parent_resource_required_if_additional(form, field):
    if form.data['is_published'] and form.data['is_additional'] and field.data is None:
        raise ValidationError('An additional resource must have a parent resource')


def no_parent_additional_resource_if_additional(form, field):
    if form.data['is_additional'] and field.data is not None and field.data['is_additional']:
        raise ValidationError('An additional resource must not have another additional resource as parent')


def no_parent_resource_if_not_additional(form, field):
    if not form.data['is_additional'] and field.data is not None:
        raise ValidationError('An standard resource must not have a parent resource')


def parent_if_not_additional(form, field):
    if form.data['is_published'] and not form.data['is_additional'] and field.data is None:
        raise ValidationError('A published standard resource must have a parent')


def no_parent_if_additional(form, field):
    if form.data['is_additional'] and field.data is not None:
        raise ValidationError('An additional resource must not have a parent')


class UserView(ProtectedModelView):
    column_list = ('full_name', 'email', 'accept_cgu', 'roles')
    form_columns = ('full_name', 'email', 'accept_cgu', 'roles')


class ResourceView(ProtectedModelView):
    column_list = (
    'is_additional', 'is_published', 'title', 'slug', 'description', 'order', 'keywords', 'parent', 'parent_resource')
    form_columns = (
    'is_additional', 'is_published', 'title', 'slug', 'description', 'order', 'keywords', 'parent', 'parent_resource',
    'resource_content')

    form_args = dict(
        parent_resource=dict(validators=[parent_resource_required_if_additional, no_parent_resource_if_not_additional,
                                         no_parent_additional_resource_if_additional]),
        parent=dict(validators=[parent_if_not_additional, no_parent_if_additional])
    )


class HierarchyTrackView(ProtectedModelView):
    column_list = ('is_active', 'is_published', 'title', 'slug', 'description', 'order', 'icon')
    form_columns = ('is_active', 'is_published', 'title', 'slug', 'description', 'order', 'icon')


class HierarchySkillView(ProtectedModelView):
    column_list = ('is_published', 'title', 'slug', 'description', 'short_description', 'track', 'order', 'icon')
    form_columns = ('is_published', 'title', 'slug', 'description', 'short_description', 'track', 'order', 'icon',
                    'validation_exercise')


class HierarchyLessonView(ProtectedModelView):
    column_list = ('is_published', 'title', 'slug', 'description', 'order', 'skill')
    form_columns = ('is_published', 'title', 'slug', 'description', 'order', 'skill')


class LocalServerView(ProtectedModelView):
    def on_model_change(self, form, model, is_created):
        if not model.secret.startswith("$2a$"):
            model.secret = self.model.hash_secret(model.secret)
        return


class StaticPageView(ProtectedModelView):
    pass


class AnalyticsView(ProtectedAdminViewMixin, BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/analytics.html")