import flask
from MookAPI import db
import datetime
import bson

class ItemToSync(db.Document):
    """A document that describes a sync operation to perform on the local server."""

    ### PROPERTIES

    queue_position = db.SequenceField()
    """An auto-incrementing counter determining the order of the operations to perform."""

    distant_id = db.ObjectIdField()
    """The ``id`` of the ``SyncableDocument`` on the central server."""

    class_name = db.StringField()
    """The class of the ``SyncableDocument`` affected by this operation."""

    action = db.StringField(choices=('update', 'delete'))
    """The operation to perform (``update`` or ``delete``)."""

    url = db.StringField()
    """The URL at which the information of the document can be downloaded. Null if ``action`` is ``delete``."""

    errors = db.ListField(db.StringField())
    """The list of the errors that occurred while trying to perform the operation."""
