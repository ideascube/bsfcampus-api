import flask
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
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill)
		
	def siblings_strict(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)
	
	def resources(self):
		return resources_documents.Resource.objects.order_by('order', 'title').filter(lesson=self)

	def to_mongo(self):
		son = super(self.__class__, self).to_mongo()
		son['resources'] = map(lambda r: r.id, self.resources())
		return son


class Skill(ResourceHierarchy):
	"""
	Second level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent track
	track = db.ReferenceField('Track')

	## icon image
	icon = db.ImageField()

	### METHODS
	
	def lessons(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self)

	def to_mongo(self):
		son = super(self.__class__, self).to_mongo()
		son['imageUrl'] = flask.url_for('hierarchy.get_skill_icon', skill_id=self.id, _external=True)
		son['bg_image_url'] = flask.url_for('hierarchy.get_track_bg_image', track_id=self.track.id, _external=True)
		son['bg_color'] = self.track.bg_color
		son['lessons'] = map(lambda l: l.id, self.lessons())
		return son


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	## thumbnail image
	image_tn = db.ImageField()

	## background image
	bg_image = db.ImageField()

	## background color
	bg_color = db.StringField()

	### METHODS
	
	def skills(self):
		return Skill.objects.order_by('order', 'title').filter(track=self)

	def to_mongo(self):
		son = super(self.__class__, self).to_mongo()
		son['image_tn_url'] = flask.url_for('hierarchy.get_track_image_tn', track_id=self.id, _external=True)
		son['bg_image_url'] = flask.url_for('hierarchy.get_track_bg_image', track_id=self.id, _external=True)
		son['skills'] = map(lambda s: s.id, self.skills())
		return son
