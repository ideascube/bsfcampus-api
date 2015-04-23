import flask
from MookAPI import db
import datetime
import bson
from slugify import slugify
from MookAPI.resources import documents as resources_documents
from MookAPI.local_server.documents import SyncableDocument


class ResourceHierarchy(SyncableDocument):
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

	### VIRTUAL PROPERTIES
	
	@property
	def track(self):
		return self.skill.track

	@property
	def url(self):
		return flask.url_for('hierarchy.get_lesson', lesson_id=self.id, _external=True)

	@property
	def resources(self):
		return resources_documents.Resource.objects.order_by('order', 'title').filter(lesson=self)

	### METHODS
	
	def siblings(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill)
		
	def siblings_strict(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)
	
	def to_mongo_detailed(self):
		son = self.to_mongo()
		son['resources'] = map(lambda r: r.id, self.resources)
		return son

	def top_level_syncable_document(self):
		return self.track

	# @if_central
	def items_to_update(self, last_sync):
		items = super(self.__class__, self).items_to_update(last_sync)

		for resource in self.resources:
			items.extend(resource.items_to_update(last_sync))

		return items


class Skill(ResourceHierarchy):
	"""
	Second level of resources hierarchy 
	"""
	
	### PROPERTIES

	## Parent track
	track = db.ReferenceField('Track')

	## icon image
	icon = db.ImageField()

	### VIRTUAL PROPERTIES
	
	@property
	def url(self):
		return flask.url_for('hierarchy.get_skill', skill_id=self.id, _external=True)

	@property
	def lessons(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self)

	### METHODS
	
	def to_mongo_detailed(self):
		son = self.to_mongo()
		son['lessons'] = map(lambda l: l.id, self.lessons)
		son['image_url'] = flask.url_for('hierarchy.get_skill_icon', skill_id=self.id, _external=True)
		son['bg_color'] = self.track.bg_color
		return son

	def top_level_syncable_document(self):
		return self.track

	# @if_central
	def items_to_update(self, last_sync):
		items = super(self.__class__, self).items_to_update(last_sync)

		for lesson in self.lessons:
			items.extend(lesson.items_to_update(last_sync))

		return items


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	## track icon
	icon = db.ImageField();

	## background color
	bg_color = db.StringField()

	### VIRTUAL PROPERTIES

	@property
	def url(self):
		return flask.url_for('hierarchy.get_track', track_id=self.id, _external=True)

	@property
	def skills(self):
		return Skill.objects.order_by('order', 'title').filter(track=self)

	### METHODS

	def to_mongo_detailed(self):
		son = self.to_mongo()
		son['skills'] = map(lambda s: s.id, self.skills)
		son['icon_url'] = flask.url_for('hierarchy.get_track_icon', track_id=self.id, _external=True)
		return son

	# @if_central
	def items_to_update(self, last_sync):
		items = super(self.__class__, self).items_to_update(last_sync)

		for skill in self.skills:
			items.extend(skill.items_to_update(last_sync))

		return items
