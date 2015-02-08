from MookAPI import db
import datetime
from ..documents import Resource

class ResourceHierarchy(db.Document):
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	### PROPERTIES

	## Title of the track
	title = db.StringField(required=True)

	## Short description of the track
	description = db.StringField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### METHODS

	def __unicode__(self):
		return self.title


class Lesson(ResourceHierarchy):
	"""
	Third level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent skill
	skill = db.ReferenceField('Skill')

	def resources(self):
		return Resource.objects(lesson=self)


class Skill(ResourceHierarchy):
	"""
	Second level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent track
	track = db.ReferenceField('Track')

	def lessons(self):
		return Lesson.objects(skill=self)


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""
	
	def skills(self):
		return Skill.objects(track=self)
