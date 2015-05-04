from MookAPI import db
from .downloadable_file import *


class VideoResourceContent(DownloadableFileResourceContent):

    ##FIXME: Override content_file to specify accepted extensions/mimetypes.

    pass


class VideoResource(DownloadableFileResource):
    """Stores a video file in the database."""

    resource_content = db.EmbeddedDocumentField(VideoResourceContent)
