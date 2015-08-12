from MookAPI.core import Service
from documents import Activity
from documents.exercise_attempt import ExerciseAttempt
from documents.skill_validation_attempt import SkillValidationAttempt
from documents.track_validation_attempt import TrackValidationAttempt
from documents.completed_resource import CompletedResource
from documents.completed_skill import CompletedSkill
from documents.completed_track import CompletedTrack
from documents.started_track import StartedTrack
from documents.unlocked_track_test import UnlockedTrackTest
from documents.visited_track import VisitedTrack
from documents.visited_skill import VisitedSkill
from documents.visited_resource import VisitedResource
from documents.visited_dashboard import VisitedDashboard
from documents.misc_activity import MiscActivity

class ActivitiesService(Service):
    __model__ = Activity

class ExerciseAttemptsService(Service):
    __model__ = ExerciseAttempt

class SkillValidationAttemptsService(Service):
    __model__ = SkillValidationAttempt

class TrackValidationAttemptsService(Service):
    __model__ = TrackValidationAttempt

class CompletedResourcesService(Service):
    __model__ = CompletedResource

class CompletedSkillsService(Service):
    __model__ = CompletedSkill

class CompletedTracksService(Service):
    __model__ = CompletedTrack

class StartedTracksService(Service):
    __model__ = StartedTrack

class UnlockedTrackTestsService(Service):
    __model__ = UnlockedTrackTest

class VisitedTrackService(Service):
    __model__ = VisitedTrack

class VisitedSkillService(Service):
    __model__ = VisitedSkill

class VisitedResourceService(Service):
    __model__ = VisitedResource

class VisitedDashboardService(Service):
    __model__ = VisitedDashboard

class MiscActivityService(Service):
    __model__ = MiscActivity
