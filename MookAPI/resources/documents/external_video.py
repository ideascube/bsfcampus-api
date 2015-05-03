from MookAPI import db
import datetime
from . import *


class ExternalVideoResourceContent(ResourceContent):

	_SOURCES = (
		'youtube',
	)
	source = db.StringField(required=True, choices=_SOURCES)
		"""The website where the video is hosted."""

	## Video unique id on the source website
	video_id = db.StringField(required=True)
		"""A unique identifier of the video on the `source` website."""


class ExternalVideoResource(Resource):
	"""References a video from the Internet."""

	resource_content = db.EmbeddedDocumentField(ExternalVideoResourceContent)
