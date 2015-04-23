import flask
from MookAPI import db
from flask.ext.security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin, login_required


class Role(db.Document, RoleMixin):

	name = db.StringField(max_length=80, unique=True)

	description = db.StringField()

	def __unicode__(self):
		return self.name


class User(db.Document, UserMixin):

	email = db.EmailField(unique=True)

	password = db.StringField()

	active = db.BooleanField(default=True)

	roles = db.ListField(db.ReferenceField(Role), default=[])

	def __unicode__(self):
		return self.email
