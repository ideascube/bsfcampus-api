from flask import url_for

from MookAPI.core import db
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument

class TutoringRelationJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class TutoringRelation(TutoringRelationJsonSerializer, SyncableDocument):
    tutor = db.ReferenceField('User')
    student = db.ReferenceField('User')
    accepted = db.BooleanField(default=False)
    acknowledged = db.BooleanField(default=False)  # has the accepted notification been seen by the initiator
    INITIATORS = ('tutor, student')
    initiated_by = db.StringField(choices=INITIATORS)

    @property
    def url(self, _external=False):
        return url_for("tutoring.get_relation", relation_id=self.id, _external=_external)
