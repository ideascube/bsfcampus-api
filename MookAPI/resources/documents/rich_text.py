from MookAPI import db
import datetime
from . import *


class RichTextResourceContent(ResourceContent):
	"""Store rich text content."""

	## HTML code of the rich text
	html = db.StringField(required=True)


class RichTextResource(Resource):
	resource_content = db.EmbeddedDocumentField(RichTextResourceContent)
