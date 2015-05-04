import flask
import documents
import MookAPI.resources.documents
import MookAPI.resources.documents.exercise_question
import json
from . import bp
from bson import json_util
import io
from flask.ext import restful
from MookAPI import api

### TRACKS

class TracksView(restful.Resource):
	def get(self):
		return documents.Track.objects.order_by('order', 'title').all()

class TrackView(restful.Resource):
	def get(self, track_id):
		return documents.Track.get_unique_object_or_404(track_id)

class TrackIconView(restful.Resource):
	def get(self, track_id):
		track = documents.Track.get_unique_object_or_404(track_id)
		
		return flask.Response(
			response=io.BytesIO(track.icon.read()),
			attachment_filename=track.icon.filename,
			mimetype=track.icon.contentType
			)

api.add_resource(TracksView, '/hierarchy/tracks', endpoint='tracks')
api.add_resource(TrackView, '/hierarchy/tracks/<track_id>', endpoint='track')
api.add_resource(TrackIconView, '/hierarchy/tracks/<track_id>/icon', endpoint='track_icon')

### SKILLS

class SkillsView(restful.Resource):
	def get(self):
		return documents.Skill.objects.order_by('order', 'title').all()

class TrackSkillsView(restful.Resource):
	def get(self, track_id):
		return documents.Skill.objects.order_by('order', 'title').filter(track=track_id)

class SkillView(restful.Resource):
	def get(self, skill_id):
		return documents.Skill.get_unique_object_or_404(skill_id)

class SkillIconView(restful.Resource):
	def get(self, skill_id):
		skill = documents.Skill.get_unique_object_or_404(skill_id)
		
		resp = flask.Response(
			response=io.BytesIO(skill.icon.read()),
			attachment_filename=skill.icon.filename,
			mimetype=skill.icon.contentType
			)

api.add_resource(SkillsView, '/hierarchy/skills', endpoint='skills')
api.add_resource(TrackSkillsView, '/hierarchy/skills/track/<track_id>', endpoint='track_skills')
api.add_resource(SkillView, '/hierarchy/skills/<skill_id>', endpoint='skill')
api.add_resource(SkillIconView, '/hierarchy/skills/<skill_id>/icon', endpoint='skill_icon')

### LESSONS

class LessonsView(restful.Resource):
	def get(self):
		return documents.Lesson.objects.order_by('order', 'title').all()

class SkillLessonsView(restful.Resource):
	def get(self, skill_id):
		return documents.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)

class LessonView(restful.Resource):
	def get(self, lesson_id):
		return documents.Lesson.get_unique_object_or_404(lesson_id)

api.add_resource(LessonsView, '/hierarchy/lessons', endpoint='lessons')
api.add_resource(SkillLessonsView, '/hierarchy/lessons/skill/<skill_id>', endpoint='skill_lessons')
api.add_resource(LessonView, '/hierarchy/lessons/<lesson_id>', endpoint='lesson')
