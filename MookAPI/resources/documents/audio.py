from MookAPI import db
import datetime
from . import *


class AudioResourceContent(ResourceContent):
	"""Reference a video from the Internet."""

	## Audio file
	audio_file = db.FileField(required=True)


class AudioResource(Resource):
	resource_content = db.EmbeddedDocumentField(AudioResourceContent)
