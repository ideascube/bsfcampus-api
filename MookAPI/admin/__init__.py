__author__ = 'FredFourcade'
from flask_admin.contrib.mongoengine import ModelView
from MookAPI.users.documents import User


class UserView(ModelView):
    column_list = ('full_name', 'username', 'email', 'password', 'accept_cgu', 'roles')
    form_columns = ('full_name', 'username', 'email', 'password', 'accept_cgu', 'roles')

    def on_model_change(self, form, model, is_created):
        model.password = User.hash_pass(model.password)
        return


class ResourceView(ModelView):
    column_list = ('title', 'slug', 'description', 'order', 'keywords', 'parent')
    form_columns = ('title', 'slug', 'description', 'order', 'keywords', 'parent', 'resource_content')

    def on_model_change(self, form, model, is_created):
        # TODO: create slug automatically
        return


class HierarchyTrackView(ModelView):
    column_list = ('title', 'slug', 'description', 'order', 'icon')
    form_columns = ('title', 'slug', 'description', 'order', 'icon')

    def on_model_change(self, form, model, is_created):
        # TODO: create slug automatically
        return


class HierarchySkillView(ModelView):
    column_list = ('title', 'slug', 'description', 'short_description', 'track', 'order', 'icon')
    form_columns = ('title', 'slug', 'description', 'short_description', 'track', 'order', 'icon', 'validation_exercise')

    def on_model_change(self, form, model, is_created):
        # TODO: create slug automatically
        return


class HierarchyLessonView(ModelView):
    column_list = ('title', 'slug', 'description', 'order', 'skill')
    form_columns = ('title', 'slug', 'description', 'order', 'skill')

    def on_model_change(self, form, model, is_created):
        # TODO: create slug automatically
        return
