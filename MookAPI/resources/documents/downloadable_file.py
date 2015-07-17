from MookAPI.core import db
from linked_file import LinkedFileResourceContentJsonSerializer, \
    LinkedFileResourceContent, \
    LinkedFileResourceJsonSerializer, \
    LinkedFileResource

class DownloadableFileResourceContentJsonSerializer(LinkedFileResourceContentJsonSerializer):
    pass

class DownloadableFileResourceContent(DownloadableFileResourceContentJsonSerializer, LinkedFileResourceContent):
    pass

class DownloadableFileResourceJsonSerializer(LinkedFileResourceJsonSerializer):
    pass

class DownloadableFileResource(DownloadableFileResourceJsonSerializer, LinkedFileResource):
    """Stores a downloadable file in the database."""

    resource_content = db.EmbeddedDocumentField(DownloadableFileResourceContent)
