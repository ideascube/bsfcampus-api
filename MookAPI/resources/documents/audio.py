from MookAPI import db
import datetime
from .downloadable_file import *


class AudioResourceContent(DownloadableFileResourceContent):
	"""Reference an audio file stored on the server."""

	##FIXME: Specify accepted extensions/mimetype on the content_file

	## Illustrative image file for the audio file
	image = db.ImageField()

	@property
	def image_url(self):
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
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
