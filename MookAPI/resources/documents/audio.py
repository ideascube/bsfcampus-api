from MookAPI import db
import datetime
from . import *


class AudioResourceContent(ResourceContent):
	"""Reference an audio file stored on the server."""

	## Audio file
	audio_file = db.FileField(required=True)


class AudioResource(Resource):
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
