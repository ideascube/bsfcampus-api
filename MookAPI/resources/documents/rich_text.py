from MookAPI.core import db
from . import ResourceContentJsonSerializer, \
    ResourceContent, \
    Resource, \
    ResourceJsonSerializer


class RichTextResourceContentJsonSerializer(ResourceContentJsonSerializer):
    pass

class RichTextResourceContent(RichTextResourceContentJsonSerializer, ResourceContent):

    html = db.StringField(required=True)
    """An HTML string containing the rich text."""


class RichTextResourceJsonSerializer(ResourceJsonSerializer):
    pass

class RichTextResource(RichTextResourceJsonSerializer, Resource):
    """Store rich text content."""

    resource_content = db.EmbeddedDocumentField(RichTextResourceContent)
