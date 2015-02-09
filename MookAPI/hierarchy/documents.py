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

	@classmethod
	def get_unique_object_or_404(cls, token, skill_token, track_token):
		if skill_token is None or track_token is None:
			try:
				bson.ObjectId(token)
			except bson.errors.InvalidId:
				abort(404)
			else:
				return cls.objects.get_or_404(id=token)
		else:
			skill = Skill.get_unique_object_or_404(skill_token, track_token)
			try:
				bson.ObjectId(token)
			except bson.errors.InvalidId:
				return cls.objects.get_or_404(slug=token, skill=skill)
			else:
				return cls.objects.get_or_404(id=token, skill=skill)


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

	@classmethod
	def get_unique_object_or_404(cls, token, track_token):
		if track_token is None:
			try:
				bson.ObjectId(token)
			except bson.errors.InvalidId:
				abort(404)
			else:
				return cls.objects.get_or_404(id=token)
		else:
			track = Track.get_unique_object_or_404(track_token)
			try:
				bson.ObjectId(token)
			except bson.errors.InvalidId:
				return cls.objects.get_or_404(slug=token, track=track)
			else:
				return cls.objects.get_or_404(id=token, track=track)


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
