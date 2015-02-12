from MookAPI import db
import datetime
import bson
from slugify import slugify
from MookAPI.resources import documents as resources_documents

class ResourceHierarchy(db.Document):
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	### PROPERTIES

	## Title
	title = db.StringField(required=True)

	## Slug (unique identifier for permalinks)
	slug = db.StringField(unique=True)

	## Short description of the track
	description = db.StringField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### METHODS

	def set_slug(self):
		pass

	def clean(self):
		self.set_slug()

	def __unicode__(self):
		return self.title

	@classmethod
	def get_unique_object_or_404(cls, token):
		try:
			bson.ObjectId(token)
		except bson.errors.InvalidId:
			return cls.objects.get_or_404(slug=token)
		else:
			return cls.objects.get_or_404(id=token)


class Lesson(ResourceHierarchy):
	"""
	Third level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent skill
	skill = db.ReferenceField('Skill')

	### METHODS

	def resources(self):
		return resources_documents.Resource.objects(lesson=self)

	def set_slug(self):
		slug = slugify(self.title) if self.slug is None else slugify(self.slug)
		def alternate_slug(text, k=1):
			return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
		k = 0
		while k < 10**4:
			if len(Lesson.objects(slug=alternate_slug(slug, k))) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k)

	


class Skill(ResourceHierarchy):
	"""
	Second level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent track
	track = db.ReferenceField('Track')

	### METHODS
	
	def lessons(self):
		return Lesson.objects(skill=self)

	def set_slug(self):
		slug = slugify(self.title) if self.slug is None else slugify(self.slug)
		def alternate_slug(text, k=1):
			return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
		k = 0
		while k < 10**4:
			if len(Skill.objects(slug=alternate_slug(slug, k))) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k)

class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	### METHODS
	
	def skills(self):
		return Skill.objects(track=self)

	def set_slug(self):
		slug = slugify(self.title) if self.slug is None else slugify(self.slug)
		def alternate_slug(text, k=1):
			return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
		k = 0
		while k < 10**4:
			if len(Track.objects(slug=alternate_slug(slug, k))) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k)
