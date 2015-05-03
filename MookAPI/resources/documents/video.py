from MookAPI import db
import datetime
from .downloadable_file import *


class VideoResourceContent(DownloadableFileResourceContent):
	"""Reference a video file stored on the server."""

	##FIXME: Specify accepted extensions/mimetype on the content_file

	pass


class VideoResource(DownloadableFileResource):
	resource_content = db.EmbeddedDocumentField(VideoResourceContent)
