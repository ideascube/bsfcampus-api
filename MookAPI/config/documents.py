import flask
from MookAPI import db
import bson
from slugify import slugify


class ConfigParameters(db.Document):

	### PROPERTIES

	## Name of the parameters group
	name = db.StringField(required=True)

	## Slug (unique identifier for permalinks)
	slug = db.StringField(unique=True)

	## Config parameters
	parameters = db.StringField(required=True)
	
	### METHODS

	def set_slug(self):
		slug = slugify(self.name) if self.slug is None else slugify(self.slug)
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
		return self.name

	@classmethod
	def get_unique_object_or_404(cls, token):
		try:
			bson.ObjectId(token)
		except bson.errors.InvalidId:
			return cls.objects.get_or_404(slug=token)
		else:
			return cls.objects.get_or_404(id=token)
