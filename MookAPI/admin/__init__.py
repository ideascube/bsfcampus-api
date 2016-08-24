from .views import *
import flask_admin as admin
import flask_login as login
from flask_wtf import form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from flask_admin import helpers, expose
from MookAPI.services import *
from MookAPI.api import _security


class LoginForm(form.Form):
    login = TextField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

    def validate_login(self, field):
        username = self.login.data
        password = self.password.data

        self.creds = _security.authenticate(username, password)

        if self.creds is None:
            raise ValidationError('Invalid user or password.')

    def get_creds(self):
        return self.creds


class CustomAdminView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(CustomAdminView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            creds = form.get_creds()
            login.login_user(creds)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(CustomAdminView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


class Admin(admin.Admin):
    def __init__(self):
        super(Admin, self).__init__(index_view=CustomAdminView(),
                                    template_mode="bootstrap3",
                                    base_template='admin/my_master.html')

        self.add_view(StaticPageView(
            static_pages.__model__,
            name='Static Pages',
            category='Misc',
            authorized_roles = ('admin',)
        ))

        self.add_view(ResourceView(
            exercise_resources.__model__,
            name='Exercise',
            category='Resources',
            authorized_roles = ('admin', 'exercice')
        ))

        self.add_view(ResourceView(
            track_validation_resources.__model__,
            name='Track Validation Test',
            category='Resources',
            authorized_roles = ('admin', 'exercice')
        ))

        self.add_view(ResourceView(
            rich_text_resources.__model__,
            name='Rich Text',
            category='Resources',
            authorized_roles = ('admin', 'contenu')
        ))

        self.add_view(ResourceView(
            audio_resources.__model__,
            name='Audio',
            category='Resources',
            authorized_roles = ('admin', 'contenu')
        ))

        self.add_view(ResourceView(
            video_resources.__model__,
            name='Video',
            category='Resources',
            authorized_roles = ('admin', 'contenu')
        ))

        self.add_view(ResourceView(
            downloadable_file_resources.__model__,
            name='Downloadable File',
            category='Resources',
            authorized_roles = ('admin', 'contenu')
        ))

        self.add_view(HierarchyTrackView(
            tracks.__model__,
            name='Track',
            category='Hierarchy',
            authorized_roles = ('admin', 'description')
        ))

        self.add_view(HierarchySkillView(
            skills.__model__,
            name='Skill',
            category='Hierarchy',
            authorized_roles = ('admin', 'description')
        ))

        self.add_view(HierarchyLessonView(
            lessons.__model__,
            name='Lesson',
            category='Hierarchy',
            authorized_roles = ('admin', 'description')
        ))

        self.add_view(UserView(
            users.__model__,
            name='User',
            category='Authentication',
            authorized_roles = ('admin',)
        ))

        self.add_view(ProtectedModelView(
            roles.__model__,
            name='Role',
            category='Authentication',
            authorized_roles = ('admin',)
        ))

        # self.add_view(ModelView(
        #     back_office_users.__model__,
        #     name='Back office user',
        #     category='Authentication'))

        self.add_view(LocalServerView(
            local_servers.__model__,
            name='Local server',
            category='Authentication',
            authorized_roles = ('admin',)
        ))

        self.add_view(AnalyticsView(
            name="Analytics",
            endpoint="admin_analytics",
            authorized_roles = ('admin', 'description')
        ))

        self.add_view(BatchLoadLocalServersView(
            name="Upload local servers",
            endpoint="upload_local_servers",
            category="Authentication",
            authorized_roles = ('admin',)
        ))
