import flask
from MookAPI import db
import datetime
import bson
from slugify import slugify
import MookAPI.mongo_coder as mc


class ResourceContent(mc.MongoCoderEmbeddedDocument):
	"""An embedded document for the actual content of the resource."""
	
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}


class Resource(mc.SyncableDocument):
	"""
	Any elementary pedagogical resource.
	Contains the metadata and a 'ResourceContent' embedded document.
	Resource objects are organized by lessons, therefore each Resource references a parent Lesson.
	"""

	meta = {
		'allow_inheritance': True,
	}
	
	### PROPERTIES

	title = db.StringField(required=True)
	"""The title of the resource."""

	slug = db.StringField(unique=True)
	"""A human-readable unique identifier for the resource."""

	## Will be implemented later
	# creator = db.ReferenceField('User')
		# """The user who created the resource."""

	description = db.StringField()
	"""A text describing the resource."""

	order = db.IntField()
	"""The order of the resource in the lesson."""

	keywords = db.ListField(db.StringField())
	"""A list of keywords to index the resource."""

	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	"""The date the resource was created."""

	lesson = db.ReferenceField('Lesson')
	"""The parent lesson."""

	resource_content = db.EmbeddedDocumentField(ResourceContent)
	"""The actual content of the resource, stored in an embedded document."""

	### VIRTUAL PROPERTIES

	@property
	def url(self):
		return flask.url_for('resources.get_resource', resource_id=self.id, _external=True)

	@property
	def is_validated(self):
		"""Whether the current user (if any) has validated this resource."""
		return False
	
	@classmethod
	def json_key(cls):
		return 'resource'

	@property
	def skill(self):
		"""Shorthand virtual property to the parent skill of the parent lesson."""
		return self.lesson.skill

	@property
	def track(self):
		"""Shorthand virtual property to the parent track of the parent skill of the parent lesson."""
		return self.lesson.skill.track
	
	### METHODS

	def siblings(self):
		"""A queryset of resources in the same lesson, including the current resource."""
		return Resource.objects.order_by('order', 'title').filter(lesson=self.lesson)
		
	def siblings_strict(self):
		"""A queryset of resources in the same lesson, excluding the current resource."""
		return Resource.objects.order_by('order', 'title').filter(lesson=self.lesson, id__ne=self.id)
		
	def aunts(self):
		"""A queryset of lessons in the same skill, including the current lesson."""
		return self.lesson.siblings()

	def aunts_strict(self):
		"""A queryset of lessons in the same skill, excluding the current lesson."""
		return self.lesson.siblings_strict()

	def cousins(self):
		"""A queryset of resources in the same skill, including the current resource."""
		return Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=self.aunts())
	
	def cousins_strict(self):
		"""A queryset of resources in the same skill, excluding the current resource."""
		return Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=self.aunts_strict())
	
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

	def encode_mongo(self):
		son = super(Resource, self).encode_mongo()

		son['breadcrumb'] = self.breadcrumb()
		son['is_validated'] = self.is_validated
		son['bg_color'] = self.track.bg_color

		return son

	def _breadcrumb_item(self):
		"""Returns some minimal information about the object for use in a breadcrumb."""

		idkey = self.__class__.json_key() + '_id'
		return {
			'title': self.title,
			'url': self.url,
			'id': self.id,
			idkey: self.id ## Deprecated. Use 'id' instead.
		}

	def breadcrumb(self):
		"""
		Returns an array of the breadcrumbs up until the current object: [Track, Skill, Lesson, Resource]
		"""

		return [
			self.track._breadcrumb_item(),
			self.skill._breadcrumb_item(),
			self.lesson._breadcrumb_item(),
			self._breadcrumb_item()
		]
		
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

	def top_level_syncable_document(self):
		return self.track
