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

	## Order of display (within sibligs)
	order = db.IntField()

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### METHODS

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

	def siblings(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)
		
	
	def resources(self):
		return resources_documents.Resource.objects.order_by('order', 'title').filter(lesson=self)


class Skill(ResourceHierarchy):
	"""
	Second level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent track
	track = db.ReferenceField('Track')

	### METHODS
	
	def lessons(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self)


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	### METHODS
	
	def skills(self):
		return Skill.objects.order_by('order', 'title').filter(track=self)
