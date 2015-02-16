from MookAPI import db
import datetime
import bson
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

	## Order of display (within sibligs)
	order = db.IntField()

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

	def siblings(self):
		return Resource.objects.order_by('order', 'title').filter(lesson=self.lesson, id__ne=self.id)
		
	def aunts(self):
		return self.lesson.siblings()

	def cousins(self):
		return Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=self.aunts())
	
	def set_slug(self):
		slug = slugify(self.title) if self.slug is None else slugify(self.slug)
		def alternate_slug(text, k=1):
			return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
		k = 0
		kmax = 10**4
		while k < kmax:
			if self.id is None:
				req = self.__class__.objects(slug=alternate_slug(slug, k))
			else:
				req = self.__class__.objects(slug=alternate_slug(slug, k), id__ne=self.id)
			if len(req) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k) if k <= kmax else None

	def clean(self):
		self.set_slug()
		
	def __unicode__(self):
		return self.title

	@classmethod
	def get_unique_object_or_404(cls, token):
		try:
			oid = bson.ObjectId(token)
		except bson.errors.InvalidId:
			return cls.objects.get_or_404(slug=token)
		else:
			return cls.objects.get_or_404(id=token)
