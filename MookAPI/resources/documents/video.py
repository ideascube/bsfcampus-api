from MookAPI.core import db
from MookAPI.utils import is_local
from .linked_file import LinkedFileResourceContentJsonSerializer, \
    LinkedFileResourceContent, \
    LinkedFileResourceJsonSerializer, \
    LinkedFileResource


class VideoResourceContentJsonSerializer(LinkedFileResourceContentJsonSerializer):

    # FIXME we should to this using the __json_*__ properties instead.
    def encode_mongo(self, fields=None, for_distant=False):
        rv = super(VideoResourceContentJsonSerializer, self).encode_mongo(
            fields=fields,
            for_distant=for_distant
        )

        if is_local():
            del rv['source']
            del rv['video_id']

        return rv

class VideoResourceContent(VideoResourceContentJsonSerializer, LinkedFileResourceContent):

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


class VideoResourceJsonSerializer(LinkedFileResourceJsonSerializer):
    pass

class VideoResource(VideoResourceJsonSerializer, LinkedFileResource):
    """Stores a video file in the database."""

    resource_content = db.EmbeddedDocumentField(VideoResourceContent)
