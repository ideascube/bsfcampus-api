from flask import url_for

from MookAPI.core import db
from .linked_file import LinkedFileResourceContentJsonSerializer, \
    LinkedFileResourceContent, \
    LinkedFileResourceJsonSerializer, \
    LinkedFileResource


class AudioResourceContentJsonSerializer(LinkedFileResourceContentJsonSerializer):
    pass

class AudioResourceContent(AudioResourceContentJsonSerializer, LinkedFileResourceContent):

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


class AudioResourceJsonSerializer(LinkedFileResourceJsonSerializer):
    pass

class AudioResource(AudioResourceJsonSerializer, LinkedFileResource):
    """Stores an audio file in the database."""
    
    resource_content = db.EmbeddedDocumentField(AudioResourceContent)
