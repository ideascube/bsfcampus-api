from MookAPI import db
import datetime
from .downloadable_file import *


class AudioResourceContent(DownloadableFileResourceContent):
	
	##FIXME: Override content_file to specify accepted extensions/mimetypes.

	## Illustrative image file for the audio file
	image = db.ImageField()
		"""An image to show with the audio player."""

	@property
	def image_url(self):
		"""The URL at which the illustration image can be downloaded."""

		if not self.image:
			return None

		if not hasattr(self, '_instance'):
			return None
			
		return flask.url_for(
			'resources.get_resource_content_image',
			resource_id=self._instance.id,
			filename=self.image.filename,
			_external=True
			)


class AudioResource(DownloadableFileResource):
	"""Stores an audio file in the database."""
	
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
