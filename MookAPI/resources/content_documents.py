from MookAPI import db
import datetime

class ResourceContent(db.EmbeddedDocument):
	"""Generic collection, every resource type will inherit from this."""
	
	meta = {
		'allow_inheritence': True,
		'abstract': True
	}

class ExternalVideoContent(ResourceContent):
	"""Reference a video from the Internet."""

	## Source website (youtube, dailymotion, vimeo, etc.)
	source = db.StringField(required=True)

	## Video unique id on the source website
	video_id = db.StringField(required=True)
