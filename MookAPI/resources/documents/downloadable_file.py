from MookAPI import db
import datetime
from . import *


class DownloadableFileResourceContent(ResourceContent):
	"""Reference a file stored on the server to be downloaded."""

	## file
	downloadable_file = db.FileField(required=True)


class DownloadableFileResource(Resource):
	resource_content = db.EmbeddedDocumentField(DownloadableFileResourceContent)
