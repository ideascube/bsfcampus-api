from MookAPI.core import Service
from .documents import Resource
from .documents.audio import AudioResource
from .documents.downloadable_file import DownloadableFileResource
from .documents.exercise import ExerciseResource
from .documents.external_video import ExternalVideoResource
from .documents.rich_text import RichTextResource
from .documents.track_validation import TrackValidationResource
from .documents.video import VideoResource


class ResourcesService(Service):
    __model__ = Resource

class AudioResourcesService(Service):
    __model__ = AudioResource

class DownloadableFileResourcesService(Service):
    __model__ = DownloadableFileResource

class ExerciseResourcesService(Service):
    __model__ = ExerciseResource

class ExternalVideoResourcesService(Service):
    __model__ = ExternalVideoResource

class RichTextResourcesService(Service):
    __model__ = RichTextResource

class TrackValidationResourcesService(Service):
    __model__ = TrackValidationResource

class VideoResourcesService(Service):
    __model__ = VideoResource
