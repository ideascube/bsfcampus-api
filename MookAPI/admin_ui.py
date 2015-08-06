from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from wtforms import ValidationError

from MookAPI.services import \
    users, \
    tracks, \
    skills, \
    lessons, \
    exercise_resources, \
    track_validation_resources, \
    rich_text_resources, \
    audio_resources, \
    video_resources, \
    downloadable_file_resources, \
    roles, \
    local_servers, \
    static_pages

# Validators
def parent_resource_required_if_additional(form, field):
    if form.data['is_additional'] and field.data is None:
        raise ValidationError('An additional resource must have a parent resource')

def no_parent_additional_resource_if_additional(form, field):
    if form.data['is_additional'] and field.data is not None and field.data['is_additional']:
        raise ValidationError('An additional resource must not have another additional resource as parent')

def no_parent_resource_if_not_additional(form, field):
    if not form.data['is_additional'] and field.data is not None:
        raise ValidationError('An standard resource must not have a parent resource')

def parent_if_not_additional(form, field):
    if not form.data['is_additional'] and field.data is None:
        raise ValidationError('An standard resource must have a parent')

def no_parent_if_additional(form, field):
    if form.data['is_additional'] and field.data is not None:
        raise ValidationError('An additional resource must not have a parent')


# Admin views
class UserView(ModelView):
    column_list = ('full_name', 'email', 'accept_cgu', 'roles')
    form_columns = ('full_name', 'email', 'accept_cgu', 'roles')

class ResourceView(ModelView):
    column_list = ('is_additional', 'title', 'slug', 'description', 'order', 'keywords', 'parent', 'parent_resource')
    form_columns = ('is_additional', 'title', 'slug', 'description', 'order', 'keywords', 'parent', 'parent_resource', 'resource_content')

    form_args = dict(
        parent_resource=dict(validators=[parent_resource_required_if_additional, no_parent_resource_if_not_additional, no_parent_additional_resource_if_additional]),
        parent=dict(validators=[parent_if_not_additional, no_parent_if_additional])
    )


class HierarchyTrackView(ModelView):
    column_list = ('title', 'slug', 'description', 'order', 'icon')
    form_columns = ('title', 'slug', 'description', 'order', 'icon')


class HierarchySkillView(ModelView):
    column_list = ('title', 'slug', 'description', 'short_description', 'track', 'order', 'icon')
    form_columns = (
    'title', 'slug', 'description', 'short_description', 'track', 'order', 'icon', 'validation_exercise')


class HierarchyLessonView(ModelView):
    column_list = ('title', 'slug', 'description', 'order', 'skill')
    form_columns = ('title', 'slug', 'description', 'order', 'skill')

class LocalServerView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.secret = self.model.hash_secret(model.secret)
        return

class StaticPageView(ModelView):
    pass


admin_ui = Admin()

admin_ui.add_view(StaticPageView(
    static_pages.__model__,
    name='Static Pages',
    category='Misc'
))

admin_ui.add_view(ResourceView(
    exercise_resources.__model__,
    name='Exercise',
    category='Resources'))

admin_ui.add_view(ResourceView(
    track_validation_resources.__model__,
    name='Track Validation Test',
    category='Resources'))

admin_ui.add_view(ResourceView(
    rich_text_resources.__model__,
    name='Rich Text',
    category='Resources'))

# admin.add_view(ResourceView(
#     external_video_resources.__model__,
#     name='External Video',
#     category='Resources'))

admin_ui.add_view(ResourceView(
    audio_resources.__model__,
    name='Audio',
    category='Resources'))

admin_ui.add_view(ResourceView(
    video_resources.__model__,
    name='Video',
    category='Resources'))

admin_ui.add_view(ResourceView(
    downloadable_file_resources.__model__,
    name='Downloadable File',
    category='Resources'))

admin_ui.add_view(HierarchyTrackView(
    tracks.__model__,
    name='Track',
    category='Hierarchy'))

admin_ui.add_view(HierarchySkillView(
    skills.__model__,
    name='Skill',
    category='Hierarchy'))

admin_ui.add_view(HierarchyLessonView(
    lessons.__model__,
    name='Lesson',
    category='Hierarchy'))

admin_ui.add_view(UserView(
    users.__model__,
    name='User',
    category='Authentication'))

admin_ui.add_view(ModelView(
    roles.__model__,
    name='Role',
    category='Authentication'))

admin_ui.add_view(LocalServerView(
    local_servers.__model__,
    name='Local server',
    category='Authentication'))
