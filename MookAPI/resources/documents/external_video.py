from MookAPI.core import db
from . import ResourceContentJsonSerializer, \
    ResourceContent, \
    Resource, \
    ResourceJsonSerializer

class ExternalVideoResourceContentJsonSerializer(ResourceContentJsonSerializer):
    pass

class ExternalVideoResourceContent(ExternalVideoResourceContentJsonSerializer, ResourceContent):

    _SOURCES = (
        'youtube',
    )
    source = db.StringField(required=True, choices=_SOURCES)
    """The website where the video is hosted."""

    ## Video unique id on the source website
    video_id = db.StringField(required=True)
    """A unique identifier of the video on the `source` website."""


class ExternalVideoResourceJsonSerializer(ResourceJsonSerializer):
    pass

class ExternalVideoResource(ExternalVideoResourceJsonSerializer, Resource):
    """References a video from the Internet."""

    resource_content = db.EmbeddedDocumentField(ExternalVideoResourceContent)
