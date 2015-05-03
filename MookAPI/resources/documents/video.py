from MookAPI import db
import datetime
from . import *


class VideoResourceContent(ResourceContent):
	"""Reference a video file stored on the server."""

	## Video file
	video_file = db.FileField(required=True)

	@property
	def video_file_url(self):
		if not self.video_file:
			return None

		if not hasattr(self, '_instance'):
			return None

		return flask.url_for(
			'resources.get_resource_content_file',
			resource_id=self._instance.id,
			filename=self.video_file.filename,
			_external=True
			)


class VideoResource(Resource):
	resource_content = db.EmbeddedDocumentField(VideoResourceContent)
