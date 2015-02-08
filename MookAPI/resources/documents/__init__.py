from MookAPI import db
import datetime
from slugify import slugify

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

	## Slug
	slug = db.StringField(unique=True)

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

	def set_slug(self):
		slug = slugify(self.title) if self.slug is None else slugify(self.slug)
		def alternate_slug(text, k=1):
			return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
		k = 0
		while k < 10**4:
			if len(Resource.objects(slug=alternate_slug(slug, k))) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k)

	def clean(self):
		self.set_slug()

	def __unicode__(self):
		return self.title
