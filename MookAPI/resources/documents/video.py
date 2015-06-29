from MookAPI.core import db
from .downloadable_file import DownloadableFileResourceContentJsonSerializer, \
    DownloadableFileResourceContent, \
    DownloadableFileResourceJsonSerializer, \
    DownloadableFileResource


class VideoResourceContentJsonSerializer(DownloadableFileResourceContentJsonSerializer):
    pass

class VideoResourceContent(DownloadableFileResourceContent):

    ##FIXME: Override content_file to specify accepted extensions/mimetypes.

    pass


class VideoResourceJsonSerializer(DownloadableFileResourceJsonSerializer):
    pass

class VideoResource(DownloadableFileResource):
    """Stores a video file in the database."""

    resource_content = db.EmbeddedDocumentField(VideoResourceContent)
