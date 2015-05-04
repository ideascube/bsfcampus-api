from MookAPI import db, api
from .downloadable_file import *
from .. import views


class AudioResourceContent(DownloadableFileResourceContent):
    
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
            
        return api.url_for(
            views.ResourceContentImageView,
            resource_id=self._instance.id,
            filename=self.image.filename,
            _external=True
            )


class AudioResource(DownloadableFileResource):
    """Stores an audio file in the database."""
    
    resource_content = db.EmbeddedDocumentField(AudioResourceContent)
