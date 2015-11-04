from .views import *
from flask.ext.admin import Admin
from MookAPI.services import *

admin = Admin(template_mode="bootstrap3")

admin.add_view(StaticPageView(
    static_pages.__model__,
    name='Static Pages',
    category='Misc'
))

admin.add_view(ResourceView(
    exercise_resources.__model__,
    name='Exercise',
    category='Resources'))

admin.add_view(ResourceView(
    track_validation_resources.__model__,
    name='Track Validation Test',
    category='Resources'))

admin.add_view(ResourceView(
    rich_text_resources.__model__,
    name='Rich Text',
    category='Resources'))

admin.add_view(ResourceView(
    audio_resources.__model__,
    name='Audio',
    category='Resources'))

admin.add_view(ResourceView(
    video_resources.__model__,
    name='Video',
    category='Resources'))

admin.add_view(ResourceView(
    downloadable_file_resources.__model__,
    name='Downloadable File',
    category='Resources'))

admin.add_view(HierarchyTrackView(
    tracks.__model__,
    name='Track',
    category='Hierarchy'))

admin.add_view(HierarchySkillView(
    skills.__model__,
    name='Skill',
    category='Hierarchy'))

admin.add_view(HierarchyLessonView(
    lessons.__model__,
    name='Lesson',
    category='Hierarchy'))

admin.add_view(UserView(
    users.__model__,
    name='User',
    category='Authentication'))

admin.add_view(ModelView(
    roles.__model__,
    name='Role',
    category='Authentication'))

# admin.add_view(ModelView(
#     back_office_users.__model__,
#     name='Back office user',
#     category='Authentication'))

admin.add_view(LocalServerView(
    local_servers.__model__,
    name='Local server',
    category='Authentication'))

admin.add_view(AnalyticsView(name="Analytics", endpoint="admin_analytics"))
