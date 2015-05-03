from MookAPI import db
import datetime
from . import *


class DownloadableFileResourceContent(ResourceContent):
	
	content_file = db.FileField(required=True)
		"""A file to download."""

	@property
	def content_file_url(self):
		"""The URL at which the file can be downloaded."""
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
	"""Stores a file in the database."""

	resource_content = db.EmbeddedDocumentField(DownloadableFileResourceContent)
