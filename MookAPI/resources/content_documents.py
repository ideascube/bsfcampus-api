from MookAPI import db
import datetime

class ResourceContent(db.DynamicEmbeddedDocument):
	"""Generic collection, every resource type will inherit from this."""
	
	meta = {
		'allow_inheritence': True,
		'abstract': True
	}


class RichTextContent(ResourceContent):
	"""Store rich text content."""

	## HTML code of the rich text
	html = db.StringField(required=True)

	def toJSONObject(self):
		ret = {}
		ret["html"] = self.html.encode('utf_8')
		return ret


class ExternalVideoContent(ResourceContent):
	"""Reference a video from the Internet."""

	## Source website (youtube, dailymotion, vimeo, etc.)
	source = db.StringField(required=True)

	## Video unique id on the source website
	video_id = db.StringField(required=True)

	def toJSONObject(self):
		ret = {}
		ret["source"] = self.source.encode('utf_8')
		ret["video_id"] = self.video_id.encode('utf_8')
		return ret
