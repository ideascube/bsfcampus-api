from MookAPI.core import db
from MookAPI import utils
from .downloadable_file import DownloadableFileResourceContentJsonSerializer, \
    DownloadableFileResourceContent, \
    DownloadableFileResourceJsonSerializer, \
    DownloadableFileResource


class VideoResourceContentJsonSerializer(DownloadableFileResourceContentJsonSerializer):
    pass

class VideoResourceContent(DownloadableFileResourceContent):

    ##FIXME: Override content_file to specify accepted extensions/mimetypes.

    _SOURCES = (
        '',
        'youtube',
    )
    source = db.StringField(choices=_SOURCES)
    """The website where the video is hosted."""

    ## Video unique id on the source website
    video_id = db.StringField()
    """A unique identifier of the video on the `source` website."""


class VideoResourceJsonSerializer(DownloadableFileResourceJsonSerializer):

    def encode_mongo(self, fields=None):
        print ("VideoResourceJsonSerializer.encode_mongo")
        rv = super(VideoResourceJsonSerializer, self).encode_mongo(fields)

        if utils.is_local():
            content = rv['resource_content']
            del content['source']
            del content['video_id']

        return rv

class VideoResource(VideoResourceJsonSerializer, DownloadableFileResource):
    """Stores a video file in the database."""

    resource_content = db.EmbeddedDocumentField(VideoResourceContent)
