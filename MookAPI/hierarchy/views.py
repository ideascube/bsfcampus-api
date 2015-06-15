import io

import flask
from flask.ext import restful
from flask.ext.security import login_required

from MookAPI import api
import documents

### TRACKS

class TracksView(restful.Resource):

    @login_required
    def get(self):
        """Get the list of all Track_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""
        
        return documents.track.Track.objects.order_by('order', 'title').all()

api.add_resource(TracksView, '/hierarchy/tracks', endpoint='tracks')


class TrackView(restful.Resource):

    @login_required
    def get(self, track_id):
        """Get the Track_ with id ``track_id`` enveloped in a single-key JSON dictionary."""

        return documents.track.Track.get_unique_object_or_404(track_id)

api.add_resource(TrackView, '/hierarchy/tracks/<track_id>', endpoint='track')


class TrackIconView(restful.Resource):
    @login_required
    def get(self, track_id):
        """Download the icon of the Track_ with id ``track_id``."""

        track = documents.track.Track.get_unique_object_or_404(track_id)

        return flask.send_file(
            io.BytesIO(track.icon.read()),
            attachment_filename=track.icon.filename,
            mimetype=track.icon.contentType
        )

api.add_resource(TrackIconView, '/hierarchy/tracks/<track_id>/icon', endpoint='track_icon')


### SKILLS

class SkillsView(restful.Resource):

    def _get_all(self):
        return documents.skill.Skill.objects.order_by('track', 'order', 'title').all()

    def _get_by_track(self, track_id):
        return documents.skill.Skill.objects.order_by('order', 'title').filter(track=track_id)
    
    @login_required
    def get(self, track_id=None):
        """
        Returns a list of all Skill_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary.
        The results are filtered by Track_ if ``track_id`` is specified.
        """

        if track_id:
            return self._get_by_track(track_id)
        else:
            return self._get_all()        

api.add_resource(
    SkillsView,
    '/hierarchy/skills', '/hierarchy/skills/track/<track_id>',
    endpoint='skills'
)


class SkillView(restful.Resource):
    
    @login_required
    def get(self, skill_id):
        """Get the Skill_ with id ``skill_id`` enveloped in a single-key JSON dictionary."""

        return documents.skill.Skill.get_unique_object_or_404(skill_id)

api.add_resource(SkillView, '/hierarchy/skills/<skill_id>', endpoint='skill')


class SkillIconView(restful.Resource):
    
    @login_required
    def get(self, skill_id):
        """Download the icon of the Skill_ with id ``skill_id``."""

        skill = documents.skill.Skill.get_unique_object_or_404(skill_id)

        return flask.send_file(
            io.BytesIO(skill.icon.read()),
            attachment_filename=skill.icon.filename,
            mimetype=skill.icon.contentType
        )

api.add_resource(SkillIconView, '/hierarchy/skills/<skill_id>/icon', endpoint='skill_icon')


### LESSONS

class LessonsView(restful.Resource):
    
    def _get_all(self):
        return documents.lesson.Lesson.objects.order_by('skill', 'order', 'title').all()

    def _get_by_skill(self, skill_id):
        return documents.lesson.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)
    
    @login_required
    def get(self, skill_id=None):
        """
        Returns a list of all Skill_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary.
        The results are filtered by Track_ if ``skill_id`` is specified.
        """

        if skill_id:
            return self._get_by_skill(skill_id)
        else:
            return self._get_all()

api.add_resource(
    LessonsView,
    '/hierarchy/lessons', '/hierarchy/lessons/skill/<skill_id>',
    endpoint='lessons'
)


class LessonView(restful.Resource):
    
    @login_required
    def get(self, lesson_id):
        """Get the Lesson_ with id ``lesson_id`` enveloped in a single-key JSON dictionary."""

        return documents.lesson.Lesson.get_unique_object_or_404(lesson_id)

api.add_resource(LessonView, '/hierarchy/lessons/<lesson_id>', endpoint='lesson')
