from MookAPI import db
import datetime

class ResourceContent(db.DynamicEmbeddedDocument):
	"""Generic collection, every resource type will inherit from this."""
	
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

class Resource(db.Document):
	"""
	Any elementary pedagogical resource.
	Contains the metadata and an embedded ResourceContent document.
	"""

	meta = {
		'allow_inheritance': True,
	}
	
	### PROPERTIES - METADATA

	## Title of the resource
	title = db.StringField(required=True)

	## Creator should reference a user
	## Will be implemented later
	# creator = db.ReferenceField('User')

	## Short description of the resource
	description = db.StringField()

	## List of keywords
	keywords = db.ListField(db.StringField())

	## Tags need to belong to a separate collection for indexation
	## Will be implemented later
	# tags = db.ListField(db.ReferenceField('ResourceTag'))

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)

	### PROPERTIES - HIERARCHY

	## Lesson
	lesson = db.ReferenceField('Lesson')
	
	### PROPERTIES - CONTENT

	## Content of the resource
	resource_content = db.EmbeddedDocumentField(ResourceContent)

	### METHODS

	def __unicode__(self):
		return self.title
