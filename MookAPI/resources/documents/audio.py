from MookAPI import db
import datetime
from . import *


class AudioResourceContent(ResourceContent):
	"""Reference an audio file stored on the server."""

	## Audio file
	audio_file = db.FileField(required=True)

	## Illustrative image file for the audio file
	image = db.ImageField()


class AudioResource(Resource):
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
