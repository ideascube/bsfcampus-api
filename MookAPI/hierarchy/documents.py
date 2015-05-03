import flask
from MookAPI import db
import datetime
import bson
from slugify import slugify
import MookAPI.mongo_coder as mc
from MookAPI.resources import documents as resources_documents


class ResourceHierarchy(mc.SyncableDocument):
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	### PROPERTIES

	title = db.StringField(required=True)
		"""The title of the hierarchy level."""

	slug = db.StringField(unique=True)
		"""A human-readable unique identifier for the hierarchy level."""

	description = db.StringField()
		"""A description of the hierarchy level."""

	order = db.IntField()
		"""The order of the hierarchy amongst its siblings."""

	date = db.DateTimeField(default=datetime.datetime.now, required=True)
		"""The date the hierarchy level was created."""

	@property
	def is_validated(self):
		"""Whether the current_user validated the hierarchy level based on their activity."""
		## Override this method in each subclass
		return False

	@property
	def progress(self):
		"""
		How many sub-units in this level have been validated (current) and how many are there in total (max).
		Returns a dictionary with format: {'current': Int, 'max': Int}
		"""
		## Override this method in each subclass
		return {'current': 0, 'max': 0}
	
	
	### METHODS

	def _set_slug(self):
		"""Sets a slug for the hierarchy level based on the title."""

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
		self._set_slug()

	def __unicode__(self):
		return self.title

	@classmethod
	def get_unique_object_or_404(cls, token):
		"""Get the only hierarchy level matching argument 'token', where 'token' can be the id or the slug."""

		try:
			bson.ObjectId(token)
		except bson.errors.InvalidId:
			return cls.objects.get_or_404(slug=token)
		else:
			return cls.objects.get_or_404(id=token)

	def __breadcrumb_item(self):
		"""Returns some minimal information about the object for use in a breadcrumb."""
		idkey = self.__class__.json_key() + '_id'
		return {
			'title': self.title,
			'url': self.url,
			'id': self.id,
			idkey: self.id ## Deprecated. Use 'id' instead.
		}

	def breadcrumb(self):
		"""Returns an array of the breadcrumbs up until the current object."""
		return []

	def encode_mongo(self):
		son = super(ResourceHierarchy, self).encode_mongo()

		son['is_validated'] = self.is_validated
		son['progress'] = self.progress
		son['breadcrumb'] = self.breadcrumb()

		return son


class Lesson(ResourceHierarchy):
	"""
	Third level of resources hierarchy 
	"""
	
	### PROPERTIES

	skill = db.ReferenceField('Skill')
		"""The parent skill."""

	### VIRTUAL PROPERTIES
	
	@property
	def track(self):
		"""The parent track of the parent skill."""
		return self.skill.track

	@property
	def url(self):
		return flask.url_for('hierarchy.get_lesson', lesson_id=self.id, _external=True)

	@property
	def resources(self):
		"""A queryset of the resources that belong to the current lesson."""
		return resources_documents.Resource.objects.order_by('order', 'title').filter(lesson=self)

	@property
	def progress(self):
		current = 0
		for resource in self.resources:
			if resource.is_validated:
				current += 1
		return {'current': current, 'max': len(self.resources)}

	### METHODS

	def breadcrumb(self):
		return [
			self.track._breadcrumb_item(),
			self.skill._breadcrumb_item(),
			self._breadcrumb_item()
			]
	
	def siblings(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill)
		
	def siblings_strict(self):
		return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)
	
	def encode_mongo(self):
		son = super(Lesson, self).encode_mongo()

		son['resources'] = map(lambda r: r.id, self.resources)

		return son

	def top_level_syncable_document(self):
		return self.track

	def all_syncable_items(self):
		items = super(Lesson, self).all_syncable_items()

		for resource in self.resources:
			items.extend(resource.all_syncable_items())

		return items

	# @if_central
	def items_to_update(self, last_sync):
		items = super(Lesson, self).items_to_update(last_sync)

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
		"""The parent track."""

	## icon image
	icon = db.ImageField()
		"""An icon to illustrate the skill."""

	@property
	def icon_url(self):
		"""The URL where the skill icon can be downloaded."""
		return flask.url_for('hierarchy.get_skill_icon', skill_id=self.id, _external=True)

	### VIRTUAL PROPERTIES
	
	@property
	def url(self):
		return flask.url_for('hierarchy.get_skill', skill_id=self.id, _external=True)

	@property
	def lessons(self):
		"""A queryset of the lessons that belong to the current skill."""
		return Lesson.objects.order_by('order', 'title').filter(skill=self)

	@property
	def progress(self):
		current = 0
		nb_resources = 0
		for lesson in self.lessons:
			for resource in lesson.resources:
				nb_resources += 1
				if resource.is_validated:
					current += 1
		return {'current': current, 'max': nb_resources}
	

	### METHODS

	def breadcrumb(self):
		return [
			self.track._breadcrumb_item(),
			self._breadcrumb_item()
			]
	
	def encode_mongo(self):
		son = super(Skill, self).encode_mongo()

		son['lessons'] = map(lambda l: l.id, self.lessons)
		son['bg_color'] = self.track.bg_color

		return son

	def top_level_syncable_document(self):
		return self.track

	def all_syncable_items(self):
		items = super(Skill, self).all_syncable_items()

		for lesson in self.lessons:
			items.extend(lesson.all_syncable_items())

		return items

	# @if_central
	def items_to_update(self, last_sync):
		items = super(Skill, self).items_to_update(last_sync)

		for lesson in self.lessons:
			items.extend(lesson.items_to_update(last_sync))

		return items


class Track(ResourceHierarchy):
	"""
	Top level of resources hierarchy 
	"""

	icon = db.ImageField()
		"""An icon to illustrate the skill."""

	@property
	def icon_url(self):
		"""The URL where the track icon can be downloaded."""
		return flask.url_for('hierarchy.get_track_icon', track_id=self.id, _external=True)

	bg_color = db.StringField()
		"""The background color of pages in this track."""

	### VIRTUAL PROPERTIES

	@property
	def url(self):
		return flask.url_for('hierarchy.get_track', track_id=self.id, _external=True)

	@property
	def skills(self):
		"""A queryset of the skills that belong to the current track."""
		return Skill.objects.order_by('order', 'title').filter(track=self)

	@property
	def progress(self):
		current = 0
		for skill in self.skills:
			if skill.is_validated:
				current += 1
		return {'current': current, 'max': len(self.skills)}
	

	### METHODS

	def breadcrumb(self):
		return [self._breadcrumb_item()]

	def encode_mongo(self):
		son = super(Track, self).encode_mongo()

		son['skills'] = map(lambda s: s.id, self.skills)

		return son

	def all_syncable_items(self):
		items = super(Track, self).all_syncable_items()

		for skill in self.skills:
			items.extend(skill.all_syncable_items())

		return items

	# @if_central
	def items_to_update(self, last_sync):
		items = super(Track, self).items_to_update(last_sync)

		for skill in self.skills:
			items.extend(skill.items_to_update(last_sync))

		return items
