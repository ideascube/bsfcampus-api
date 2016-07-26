from .views import *
from flask.ext.admin import Admin as BaseAdmin
from MookAPI.services import *

class Admin(BaseAdmin):
    def __init__(self):
        BaseAdmin.__init__(self, template_mode="bootstrap3")

        self.add_view(StaticPageView(
            static_pages.__model__,
            name='Static Pages',
            category='Misc'
        ))

        self.add_view(ResourceView(
            exercise_resources.__model__,
            name='Exercise',
            category='Resources'))

        self.add_view(ResourceView(
            track_validation_resources.__model__,
            name='Track Validation Test',
            category='Resources'))

        self.add_view(ResourceView(
            rich_text_resources.__model__,
            name='Rich Text',
            category='Resources'))

        self.add_view(ResourceView(
            audio_resources.__model__,
            name='Audio',
            category='Resources'))

        self.add_view(ResourceView(
            video_resources.__model__,
            name='Video',
            category='Resources'))

        self.add_view(ResourceView(
            downloadable_file_resources.__model__,
            name='Downloadable File',
            category='Resources'))

        self.add_view(HierarchyTrackView(
            tracks.__model__,
            name='Track',
            category='Hierarchy'))

        self.add_view(HierarchySkillView(
            skills.__model__,
            name='Skill',
            category='Hierarchy'))

        self.add_view(HierarchyLessonView(
            lessons.__model__,
            name='Lesson',
            category='Hierarchy'))

        self.add_view(UserView(
            users.__model__,
            name='User',
            category='Authentication'))

        self.add_view(ModelView(
            roles.__model__,
            name='Role',
            category='Authentication'))

        # self.add_view(ModelView(
        #     back_office_users.__model__,
        #     name='Back office user',
        #     category='Authentication'))

        self.add_view(LocalServerView(
            local_servers.__model__,
            name='Local server',
            category='Authentication'))

        self.add_view(AnalyticsView(name="Analytics", endpoint="admin_analytics"))

        self.add_view(BatchLoadLocalServersView(name="Upload local servers", endpoint="upload_local_servers", category="Authentication"))
