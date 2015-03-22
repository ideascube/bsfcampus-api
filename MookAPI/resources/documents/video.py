from MookAPI import db
import datetime
from . import *


class VideoResourceContent(ResourceContent):
	"""Reference a video file stored on the server."""

	## Video file
	video_file = db.FileField(required=True)


class VideoResource(Resource):
	resource_content = db.EmbeddedDocumentField(VideoResourceContent)
