from MookAPI import db
import datetime
from . import *


class AudioResourceContent(ResourceContent):
	"""Reference an audio file stored on the server."""

	## Audio file
	audio_file = db.FileField(required=True)

	@property
	def audio_file_url(self):
		if not self.audio_file:
			return None

		if not hasattr(self, '_instance'):
			return None

		return flask.url_for(
			'resources.get_resource_content_file',
			resource_id=self._instance.id,
			filename=self.audio_file.filename,
			_external=True
			)
	

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


class AudioResource(Resource):
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
