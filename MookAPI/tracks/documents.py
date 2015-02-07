from MookAPI import db
import datetime

from ..resources import documents as resources_documents


class Lesson(db.EmbeddedDocument):
	"""
	Third-level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Title of the track
	title = db.StringField(required=True)

	## Short description of the track
	description = db.StringField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### PROPERTIES - CHILDREN ELEMENTS

	## Resources in the lesson
	resources = db.ListField(db.ReferenceField(resources_documents.Resource))

	### METHODS

	def __unicode__(self):
		return self.title


class Skill(db.EmbeddedDocument):
	"""
	Second-level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Title of the track
	title = db.StringField(required=True)

	## Short description of the track
	description = db.StringField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### PROPERTIES - CHILDREN ELEMENTS

	## Lessons in the skill
	lessons = db.ListField(db.EmbeddedDocumentField(Lesson))

	### METHODS

	def __unicode__(self):
		return self.title

class Track(db.Document):
	"""
	Top-level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Title of the track
	title = db.StringField(required=True)

	## Short description of the track
	description = db.StringField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### PROPERTIES - CHILDREN ELEMENTS

	## Skills in the track
	skills = db.ListField(db.EmbeddedDocumentField(Skill))

	### METHODS

	def __unicode__(self):
		return self.title
