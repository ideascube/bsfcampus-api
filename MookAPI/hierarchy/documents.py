from MookAPI import db
import datetime
from slugify import slugify
from MookAPI.resources import documents as resources_documents

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

	def set_slug(self):
		pass

	def clean(self):
		self.set_slug()

	def __unicode__(self):
		return self.title


class Lesson(ResourceHierarchy):
	"""
	Third level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Slug
	slug = db.StringField(required=True, unique_with='skill')

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
			if len(Lesson.objects(slug=alternate_slug(slug, k), skill=self.skill)) > 0:
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

	## Slug
	slug = db.StringField(required=True, unique_with='track')

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
			if len(Skill.objects(slug=alternate_slug(slug, k), track=self.track)) > 0:
				k = k + 1
				continue
			else:
				break
		self.slug = alternate_slug(slug, k)


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	### PROPERTIES

	## Slug
	slug = db.StringField(required=True, unique=True)
	
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
