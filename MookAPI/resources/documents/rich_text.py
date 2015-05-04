from MookAPI import db
from . import *


class RichTextResourceContent(ResourceContent):

    html = db.StringField(required=True)
    """An HTML string containing the rich text."""


class RichTextResource(Resource):
    """Store rich text content."""

    resource_content = db.EmbeddedDocumentField(RichTextResourceContent)
