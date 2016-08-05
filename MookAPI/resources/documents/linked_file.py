from flask import url_for

from MookAPI.core import db
from . import ResourceContentJsonSerializer, \
    ResourceContent, \
    ResourceJsonSerializer, \
    Resource

class LinkedFileResourceContentJsonSerializer(ResourceContentJsonSerializer):
    __json_files__ = ['content_file']

class LinkedFileResourceContent(LinkedFileResourceContentJsonSerializer, ResourceContent):

    content_file = db.StringField()
    """
    The URL or the name of the file to download.
    If an absolute URL (containing "://" or starting with "//" is given, that URL will be used as the source.
    Otherwise, the string will be interpreted as a path from the "static" folder.
    """

    def clean(self):
        super(LinkedFileResourceContent, self).clean()
        self.content_file = self.content_file.strip()

class LinkedFileResourceJsonSerializer(ResourceJsonSerializer):
    pass

class LinkedFileResource(Resource):
    """Stores a file in the database."""

    resource_content = db.EmbeddedDocumentField(LinkedFileResourceContent)
