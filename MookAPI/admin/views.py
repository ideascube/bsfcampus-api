import datetime
import io
import os

from wtforms import ValidationError

from flask import abort, redirect, url_for, request, Response

from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import BaseView, expose
from flask_login import current_user
from MookAPI.services import activities, users, tracks, skills, lessons
from MookAPI.serialization import UnicodeCSVWriter
from mongoengine.common import _import_class

from collections import defaultdict
import pygal


from bson import DBRef
from jinja2 import Markup

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
    list_formatters = dict(full_name=lambda v, c, m, p: Markup(u"<a href='/admin/user/info/{u.id}'>{u.full_name}</a>".format(u=m)))

    @expose('/info/<user_id>')
    def user_info(self, user_id):
        user = users.get_or_404(user_id)
        return self.render("admin/user_info.html", user=user, tracks=tracks, skills=skills, lessons=lessons)

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

    @expose("/user.csv")
    def get_prepared_analytics(self):
        """
        Returns a .csv file with all the activities which took place between the start_date and the end_date
        """
        start_date_arg = request.args.get('start_date', None)
        if start_date_arg is None:
            start_date = datetime.datetime.fromtimestamp(0)
        else:
            start_date = datetime.datetime.strptime(start_date_arg, "%Y-%m-%d").date()

        end_date_arg = request.args.get('end_date', None)
        if end_date_arg is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(end_date_arg, "%Y-%m-%d").date() + datetime.timedelta(days=1)

        file_name = "users_"
        file_name += (start_date_arg or "begining") + "_" + (end_date_arg or "now")
        file_name += ".csv"

        all_users = activities.__model__.objects.filter(date__gte=start_date, date__lte=end_date).only('user').distinct('user')

        def write():
            analytics_writer = UnicodeCSVWriter()
            yield analytics_writer.csv_row_serialize(users.__model__.field_names_header_for_csv())
            for user in all_users:
                if isinstance(user, DBRef):
                    continue
                d = analytics_writer.csv_object_serialize(user)
                yield d

        response = Response(write())
        response.headers['Content-Disposition'] = "attachment; filename=%s"%file_name
        response.headers['Content-type'] = 'text/csv'

        return response

    @expose("/user_graph.svg")
    def get_user_graph(self):
        """
        Returns a .svg graph with the user visits.
        """
        start_date_arg = request.args.get('start_date', "2016-05-01")
        if start_date_arg is None:
            start_date = datetime.datetime.fromtimestamp(0)
        else:
            start_date = datetime.datetime.strptime(start_date_arg, "%Y-%m-%d").date()

        end_date_arg = request.args.get('end_date', None)
        if end_date_arg is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(end_date_arg, "%Y-%m-%d").date() + datetime.timedelta(days=1)

        by_day = request.args.get('by_day', False)
        if by_day:
            time_str = 'day'
            get_key = lambda a: a.date()
            format_x_label = lambda d : d
        else:
            time_str = 'week'
            get_key = lambda a: a.isocalendar()[:-1]
            format_x_label = lambda d : "Week %d, year %d"%(d[::-1])

        activities_ = activities.__model__.objects.filter(date__gte=start_date, date__lte=end_date).only('date', 'user')

        activities_ = ( (get_key(i.date), i.user) for i in activities_)
        res = defaultdict(set)
        for key, v in activities_:
            res[key].add(v)

        res = sorted((k,len(v)) for k,v in res.items())

        chart = pygal.Bar(show_legend=False,
                          explicit_size=False,
                          x_label_rotation=50,
                          style=pygal.style.BlueStyle)
        chart.x_labels = [format_x_label(i[0]) for i in res]
        chart.add('user per %s'%time_str, [i[1] for i in res])

        return chart.render_response()


class BatchLoadLocalServersView(ProtectedAdminViewMixin, BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/load_local_servers.html")
