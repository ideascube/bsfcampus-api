from flask import url_for

from MookAPI.core import db
from .downloadable_file import DownloadableFileResourceContentJsonSerializer, \
    DownloadableFileResourceContent, \
    DownloadableFileResourceJsonSerializer, \
    DownloadableFileResource


class AudioResourceContentJsonSerializer(DownloadableFileResourceContentJsonSerializer):
    pass

class AudioResourceContent(AudioResourceContentJsonSerializer, DownloadableFileResourceContent):

    ##FIXME: Override content_file to specify accepted extensions/mimetypes.

    ## Illustrative image file for the audio file
    image = db.ImageField()
    """An image to show with the audio player."""

    @property
    def image_url(self):
        """The URL at which the illustration image can be downloaded."""

        if not self.image:
            return None

        if not hasattr(self, '_instance'):
            return None

        return url_for(
            "resources.get_resource_content_image",
            resource_id=self._instance.id,
            filename=self.image.filename,
            _external=True
        )


class AudioResourceJsonSerializer(DownloadableFileResourceJsonSerializer):
    pass

class AudioResource(AudioResourceJsonSerializer, DownloadableFileResource):
    """Stores an audio file in the database."""
    
    resource_content = db.EmbeddedDocumentField(AudioResourceContent)
