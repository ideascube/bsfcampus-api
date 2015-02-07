from MookAPI import db
import datetime
from . import *

class ExternalVideoResourceContent(ResourceContent):
	"""Reference a video from the Internet."""

	## Source website (youtube, dailymotion, vimeo, etc.)
	SOURCES = (
		'youtube',
	)
	source = db.StringField(required=True, choices=SOURCES)

	## Video unique id on the source website
	video_id = db.StringField(required=True)

class ExternalVideoResource(Resource):
	resource_content = db.EmbeddedDocumentField(ExternalVideoResourceContent)
