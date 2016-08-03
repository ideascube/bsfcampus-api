from wtforms import ValidationError

from flask import abort, redirect, url_for, request

from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import BaseView, expose
from flask_login import current_user

class ProtectedAdminViewMixin(object):
    def __init__(self, *args, **kwargs):
        authorized_roles = kwargs.pop('authorized_roles', [])
        super(ProtectedAdminViewMixin, self).__init__(*args, **kwargs)
        self.authorized_roles = authorized_roles

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        for role in self.authorized_roles:
            if current_user.has_role(role):
                return True

        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        if not current_user.is_anonymous:
            abort(403)
        else:
            return redirect(url_for('admin.login_view', next=request.url))


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
    column_searchable_list = ('full_name', 'email')
    column_list = ('full_name', 'email', 'accept_cgu', 'roles')
    form_columns = ('full_name', 'email', 'accept_cgu', 'roles')


class ResourceView(ProtectedModelView):
    column_searchable_list = ('title', 'slug', 'description')
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
    column_searchable_list = ('title', 'slug', 'description')
    column_list = ('is_active', 'is_published', 'title', 'slug', 'description', 'order', 'icon')
    form_columns = ('is_active', 'is_published', 'title', 'slug', 'description', 'order', 'icon')


class HierarchySkillView(ProtectedModelView):
    column_searchable_list = ('title', 'slug', 'description')
    column_list = ('is_published', 'title', 'slug', 'description', 'short_description', 'track', 'order', 'icon')
    form_columns = ('is_published', 'title', 'slug', 'description', 'short_description', 'track', 'order', 'icon',
                    'validation_exercise')


class HierarchyLessonView(ProtectedModelView):
    column_searchable_list = ('title', 'slug', 'description')
    column_list = ('is_published', 'title', 'slug', 'description', 'order', 'skill')
    form_columns = ('is_published', 'title', 'slug', 'description', 'order', 'skill')


class LocalServerView(ProtectedModelView):
    column_searchable_list = ('name', 'key')
    def on_model_change(self, form, model, is_created):
        if not model.secret.startswith("$2a$"):
            model.secret = self.model.hash_secret(model.secret)
        return


class StaticPageView(ProtectedModelView):
    column_searchable_list = ('page_id', 'html_content')


class AnalyticsView(ProtectedAdminViewMixin, BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/analytics.html")


class BatchLoadLocalServersView(ProtectedAdminViewMixin, BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/load_local_servers.html")
