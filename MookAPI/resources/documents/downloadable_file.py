from MookAPI import db
import datetime
from . import *


class DownloadableFileResourceContent(ResourceContent):
	"""Reference a file stored on the server to be downloaded."""

	## file
	content_file = db.FileField(required=True)

	@property
	def content_file_url(self):
		if not self.content_file:
			return None

		if not hasattr(self, '_instance'):
			return None

		return flask.url_for(
			'resources.get_resource_content_file',
			resource_id=self._instance.id,
			filename=self.content_file.filename,
			_external=True
			)


class DownloadableFileResource(Resource):
	resource_content = db.EmbeddedDocumentField(DownloadableFileResourceContent)
