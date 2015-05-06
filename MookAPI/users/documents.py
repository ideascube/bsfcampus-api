import flask
from MookAPI import db
from flask.ext.security import Security, UserMixin, RoleMixin


class Role(db.Document, RoleMixin):

    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name


class User(db.Document, UserMixin):

    first_name = db.StringField()

    last_name = db.StringField()

    username = db.StringField() # To make this unique we first need to update the registration form to include the field.

    email = db.EmailField(unique=True)

    password = db.StringField()

    active = db.BooleanField(default=True)

    roles = db.ListField(db.ReferenceField(Role), default=[])

    def __unicode__(self):
        return self.email
